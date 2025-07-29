import os
from fastapi import FastAPI, Request, Body
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import requests
import sqlite3
from dotenv import load_dotenv
from appointment_utils import create_appointment, save_user_memory, load_user_memory
from hf_utils import hf_intent_classification, hf_sentiment_analysis, llama3_chat_completion
from whisper_utils import whisper_transcribe
from tts_utils import coqui_tts
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Form
import pathlib
import json
from datetime import datetime, timedelta
import uuid

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client for outbound calls
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simple in-memory session state (for demo) ---
session_state = {}

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    # Appointments table
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        datetime TEXT,
        service TEXT,
        notes TEXT,
        status TEXT DEFAULT 'scheduled',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Call logs table
    c.execute('''CREATE TABLE IF NOT EXISTS call_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_id TEXT UNIQUE,
        phone_number TEXT,
        user_name TEXT,
        conversation_data TEXT,
        intent TEXT,
        sentiment TEXT,
        duration_seconds INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # System prompts table
    c.execute('''CREATE TABLE IF NOT EXISTS system_prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scenario_name TEXT UNIQUE,
        prompt_text TEXT,
        is_active BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insert default system prompt
    c.execute('''INSERT OR IGNORE INTO system_prompts (scenario_name, prompt_text, is_active) 
                  VALUES (?, ?, ?)''', 
              ('default', 
               'You are a friendly and clear-speaking AI assistant for a medical appointment booking system. Always respond in a polite and casual tone. Keep your replies short, helpful, and easy to speak aloud. Help users book, reschedule, or cancel appointments, and answer questions about services.',
               1))
    
    conn.commit()
    conn.close()

init_db()

# Set up Jinja2 templates directory
BASE_DIR = pathlib.Path(__file__).parent.resolve()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --- Helper Functions ---
def log_call(phone_number, user_name, conversation_data, intent, sentiment, duration_seconds=0):
    """Log call details to database"""
    call_id = str(uuid.uuid4())
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''INSERT INTO call_logs 
                  (call_id, phone_number, user_name, conversation_data, intent, sentiment, duration_seconds)
                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (call_id, phone_number, user_name, json.dumps(conversation_data), intent, sentiment, duration_seconds))
    conn.commit()
    conn.close()
    return call_id

def get_active_system_prompt():
    """Get the currently active system prompt"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('SELECT prompt_text FROM system_prompts WHERE is_active = 1 LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result[0] if result else "You are a helpful AI assistant."

def update_system_prompt(scenario_name, prompt_text, make_active=False):
    """Create or update a system prompt"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    if make_active:
        # Deactivate all other prompts
        c.execute('UPDATE system_prompts SET is_active = 0')
    
    c.execute('''INSERT OR REPLACE INTO system_prompts (scenario_name, prompt_text, is_active)
                  VALUES (?, ?, ?)''', (scenario_name, prompt_text, 1 if make_active else 0))
    
    conn.commit()
    conn.close()

def make_reminder_call(phone_number, appointment_data):
    """Make an outbound reminder call"""
    if not twilio_client:
        return {"error": "Twilio client not configured"}
    
    try:
        # Create TwiML for the reminder call
        reminder_message = f"""
        Hello {appointment_data['name']}, this is your appointment reminder. 
        You have an appointment scheduled for {appointment_data['datetime']} for {appointment_data['service']}. 
        Please call us if you need to reschedule. Thank you!
        """
        
        # Make the call
        call = twilio_client.calls.create(
            url=f"http://localhost:8000/twilio/reminder-webhook",
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            method='POST',
            status_callback=f"http://localhost:8000/twilio/status-callback",
            status_callback_event=['completed'],
            status_callback_method='POST'
        )
        
        return {"success": True, "call_sid": call.sid, "message": "Reminder call initiated"}
    
    except Exception as e:
        return {"error": f"Failed to make reminder call: {str(e)}"}

def get_upcoming_appointments(hours_ahead=24):
    """Get appointments scheduled within the next X hours"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    # Get appointments in the next X hours
    now = datetime.now()
    future_time = now + timedelta(hours=hours_ahead)
    
    # Format dates for SQL comparison
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    future_str = future_time.strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('''SELECT id, name, phone, datetime, service, notes, status 
                  FROM appointments 
                  WHERE datetime >= ? AND datetime <= ? AND status = 'scheduled'
                  ORDER BY datetime''', 
              (now_str, future_str))
    
    appointments = []
    for row in c.fetchall():
        appointments.append({
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'datetime': row[3],
            'service': row[4],
            'notes': row[5],
            'status': row[6]
        })
    
    conn.close()
    return appointments

# --- Admin Routes ---
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    """Admin dashboard main page"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/admin/appointments", response_class=HTMLResponse)
def admin_appointments(request: Request):
    """Admin appointments management page"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''SELECT id, name, phone, datetime, service, notes, status, created_at 
                  FROM appointments ORDER BY created_at DESC''')
    appointments = c.fetchall()
    conn.close()
    
    return templates.TemplateResponse("admin_appointments.html", {
        "request": request, 
        "appointments": appointments
    })

@app.get("/admin/calls", response_class=HTMLResponse)
def admin_calls(request: Request):
    """Admin call logs page"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''SELECT id, call_id, phone_number, user_name, conversation_data, 
                         intent, sentiment, duration_seconds, created_at 
                  FROM call_logs ORDER BY created_at DESC''')
    calls = c.fetchall()
    conn.close()
    
    return templates.TemplateResponse("admin_calls.html", {
        "request": request, 
        "calls": calls
    })

@app.get("/admin/prompts", response_class=HTMLResponse)
def admin_prompts(request: Request):
    """Admin page for managing AI prompts"""
    return templates.TemplateResponse("admin_prompts.html", {"request": request})

@app.get("/admin/reminders", response_class=HTMLResponse)
def admin_reminders(request: Request):
    """Admin page for managing reminder calls"""
    return templates.TemplateResponse("admin_reminders.html", {"request": request})

# --- Admin API Endpoints ---
@app.get("/api/admin/appointments")
def get_appointments_api():
    """Get all appointments as JSON"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''SELECT id, name, phone, datetime, service, notes, status, created_at 
                  FROM appointments ORDER BY created_at DESC''')
    appointments = c.fetchall()
    conn.close()
    
    return {
        "appointments": [
            {
                "id": row[0],
                "name": row[1],
                "phone": row[2],
                "datetime": row[3],
                "service": row[4],
                "notes": row[5],
                "status": row[6],
                "created_at": row[7]
            }
            for row in appointments
        ]
    }

@app.get("/api/admin/calls")
def get_calls_api():
    """Get all call logs as JSON"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''SELECT id, call_id, phone_number, user_name, conversation_data, 
                         intent, sentiment, duration_seconds, created_at 
                  FROM call_logs ORDER BY created_at DESC''')
    calls = c.fetchall()
    conn.close()
    
    return {
        "calls": [
            {
                "id": row[0],
                "call_id": row[1],
                "phone_number": row[2],
                "user_name": row[3],
                "conversation_data": json.loads(row[4]) if row[4] else [],
                "intent": row[5],
                "sentiment": row[6],
                "duration_seconds": row[7],
                "created_at": row[8]
            }
            for row in calls
        ]
    }

@app.get("/api/admin/prompts")
def get_prompts_api():
    """Get all system prompts as JSON"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('SELECT id, scenario_name, prompt_text, is_active, created_at FROM system_prompts')
    prompts = c.fetchall()
    conn.close()
    
    return {
        "prompts": [
            {
                "id": row[0],
                "scenario_name": row[1],
                "prompt_text": row[2],
                "is_active": bool(row[3]),
                "created_at": row[4]
            }
            for row in prompts
        ]
    }

@app.post("/api/admin/prompts")
def create_prompt_api(data: dict = Body(...)):
    """Create or update a system prompt"""
    scenario_name = data.get("scenario_name")
    prompt_text = data.get("prompt_text")
    make_active = data.get("make_active", False)
    
    if not scenario_name or not prompt_text:
        return JSONResponse({"error": "Missing required fields"}, status_code=400)
    
    update_system_prompt(scenario_name, prompt_text, make_active)
    return {"status": "success", "message": "Prompt updated successfully"}

@app.put("/api/admin/appointments/{appointment_id}")
def update_appointment_api(appointment_id: int, data: dict = Body(...)):
    """Update appointment status"""
    status = data.get("status")
    if not status:
        return JSONResponse({"error": "Status is required"}, status_code=400)
    
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Appointment updated successfully"}

# --- Existing Routes ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    from appointment_utils import get_appointments
    appointments = get_appointments()
    return templates.TemplateResponse("list.html", {"request": request, "appointments": appointments})

@app.get("/appointments/new", response_class=HTMLResponse)
def new_appointment_form(request: Request):
    return templates.TemplateResponse("new.html", {"request": request})

@app.post("/appointments/new")
def create_appointment_form(request: Request, name: str = Form(...), phone: str = Form(...), datetime: str = Form(...), notes: str = Form("")):
    from appointment_utils import create_appointment
    create_appointment(name, phone, datetime, notes)
    return RedirectResponse(url="/", status_code=303)

@app.post("/appointments/{appointment_id}/delete")
def delete_appointment_form(appointment_id: int):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/twilio/webhook", response_class=PlainTextResponse)
async def twilio_webhook(request: Request):
    print("Twilio webhook called")
    resp = VoiceResponse()
    call_start_time = datetime.now()
    conversation_data = []
    
    try:
        form = await request.form()
        print("Form data received:", form)
        speech_result = form.get('SpeechResult')
        from_number = form.get('From')
        attempt = int(form.get('attempt', 1)) if 'attempt' in form else 1
        
        # --- Persistent memory: Load from DB if not in session ---
        if from_number not in session_state:
            user_memory = load_user_memory(from_number)
            session_state[from_number] = {'history': user_memory, 'step': 'greet'}
        state = session_state[from_number]

        # --- Step 1: Service Introduction ---
        if state["step"] == "greet":
            gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
            gather.say('Welcome to Smart Appointment Services! I am your virtual assistant. I can help you book, reschedule, or cancel appointments, and answer questions about our services. How can I help you today?')
            resp.append(gather)
            resp.say('I did not hear anything. Please say if you want to book, reschedule, or cancel an appointment, or ask about our services.')
            session_state[from_number] = {"step": "intent"}
            
            # Log the greeting
            conversation_data.append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "ai",
                "message": "Welcome to Smart Appointment Services! I am your virtual assistant. I can help you book, reschedule, or cancel appointments, and answer questions about our services. How can I help you today?"
            })
            
            return str(resp)

        # --- Step 2: Intent Recognition & Service Options ---
        if state["step"] == "intent":
            if not speech_result:
                if attempt < 2:
                    gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                    gather.say('Please say if you want to book, reschedule, or cancel an appointment, or ask about our services.')
                    resp.append(gather)
                    resp.say('I did not hear anything. Please say your intent after the beep.')
                    return str(resp)
                else:
                    resp.say('I did not hear anything. Please call again if you need assistance. Goodbye!')
                    resp.hangup()
                    session_state.pop(from_number, None)
                    return str(resp)
            
            # Log user input
            conversation_data.append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "user",
                "message": speech_result
            })
            
            # --- Enhanced: Detect intent and sentiment ---
            intent_result = hf_intent_classification(speech_result)
            sentiment_result = hf_sentiment_analysis(speech_result)
            
            # Extract intent and sentiment labels (fallback to 'unknown' if not found)
            intent_label = None
            if isinstance(intent_result, dict):
                if 'error' in intent_result:
                    intent_label = 'unknown'
                elif isinstance(intent_result, list) and len(intent_result) > 0 and 'label' in intent_result[0]:
                    intent_label = intent_result[0]['label']
                elif 'label' in intent_result:
                    intent_label = intent_result['label']
            if not intent_label:
                # fallback to keyword logic
                intent_label = "book" if "book" in speech_result.lower() else ("reschedule" if "reschedule" in speech_result.lower() else ("cancel" if "cancel" in speech_result.lower() else ("service" if "service" in speech_result.lower() or "offer" in speech_result.lower() else "unknown")))
            
            sentiment_label = None
            if isinstance(sentiment_result, dict):
                if 'error' in sentiment_result:
                    sentiment_label = 'neutral'
                elif isinstance(sentiment_result, list) and len(sentiment_result) > 0 and 'label' in sentiment_result[0]:
                    sentiment_label = sentiment_result[0]['label']
                elif 'label' in sentiment_result:
                    sentiment_label = sentiment_result['label']
            if not sentiment_label:
                sentiment_label = 'neutral'
            
            # --- Advanced Memory: Store rolling history of last 5 user inputs, intents, sentiments ---
            session_state[from_number] = session_state.get(from_number, {})
            history = session_state[from_number].get('history', [])
            history.append({
                'input': speech_result,
                'intent': intent_label,
                'sentiment': sentiment_label
            })
            if len(history) > 5:
                history = history[-5:]
            session_state[from_number]['history'] = history
            
            # Save persistent memory after each turn
            save_user_memory(from_number, history)
            
            # Build a memory string for Llama 3
            memory_str = ''
            for h in history[:-1]:
                memory_str += f"User said: '{h['input']}' (intent: {h['intent']}, sentiment: {h['sentiment']}).\n"
            
            # --- Enhanced: Build system prompt for Llama 3 with memory ---
            system_prompt = get_active_system_prompt()
            enhanced_prompt = f"""
{system_prompt}

The user intent is {intent_label}, and the user sentiment is {sentiment_label}. If the user seems negative or angry, soften your tone and show empathy. If the user is happy, sound more cheerful. Use simple, human-friendly words. Add polite conversational fillers like 'sure!', 'got it!', or 'let me check!' to make the tone more friendly. Break long answers into short sentences (ideally under 15 words) so the TTS sounds natural. Here is some context from earlier in the conversation: {memory_str} User: {speech_result} Assistant:"""
            
            # --- Enhanced: Get Llama 3 response ---
            ai_response = llama3_chat_completion(speech_result, system_prompt=enhanced_prompt)
            
            # --- Fallback logic if Llama 3 fails ---
            if not ai_response or 'Sorry, I could not process' in ai_response or len(ai_response.strip()) < 2:
                ai_response = "Hmm, I'm still learning that. Would you like me to search more?"
            
            # Log AI response
            conversation_data.append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "ai",
                "message": ai_response
            })
            
            # --- Enhanced: Post-process for TTS ---
            import re
            def split_sentences(text):
                # Split on period, exclamation, question, or long comma pauses
                return [s.strip() for s in re.split(r'[.!?\n]|(?<=,)', text) if s.strip()]
            
            def add_filler(sentence, sentiment):
                if sentiment in ['negative', 'angry', 'sad']:
                    return "I'm here to help. " + sentence
                elif sentiment in ['positive', 'happy']:
                    return "Sure! " + sentence
                else:
                    return sentence
            
            sentences = split_sentences(ai_response)
            
            # If user says goodbye/bye, end the call, else keep the session open for more questions
            end_keywords = ['goodbye', 'bye', 'see you', 'exit', 'quit']
            if any(kw in speech_result.lower() for kw in end_keywords):
                for i, s in enumerate(sentences[:4]):
                    s = add_filler(s, sentiment_label)
                    resp.say(s)
                resp.hangup()
                session_state.pop(from_number, None)
                
                # Log the call
                call_duration = (datetime.now() - call_start_time).seconds
                log_call(from_number, "Unknown", conversation_data, intent_label, sentiment_label, call_duration)
                
                return str(resp)
            else:
                gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                for i, s in enumerate(sentences[:4]):
                    s = add_filler(s, sentiment_label)
                    gather.say(s)
                gather.say("If you have another question, please speak after the beep. Or say 'goodbye' to end the call.")
                resp.append(gather)
                session_state[from_number]["step"] = "intent"
                return str(resp)

        # --- Step 3: Ask for Service Type ---
        if state["step"] == "ask_service":
            if not speech_result:
                gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                gather.say('Please say the service you want to book, like consultation, check-up, or therapy session.')
                resp.append(gather)
                return str(resp)
            session_state[from_number] = {"step": "ask_datetime", "service": speech_result}
            gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
            gather.say('Thank you. What date and time would you like your appointment?')
            resp.append(gather)
            return str(resp)

        # --- Step 4: Ask for Date/Time ---
        if state["step"] == "ask_datetime":
            if not speech_result:
                gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                gather.say('Please say the date and time for your appointment.')
                resp.append(gather)
                return str(resp)
            session_state[from_number] = {"step": "ask_name", "service": state.get("service", "General"), "datetime": speech_result}
            gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
            gather.say('Thank you. Can I have your name, please?')
            resp.append(gather)
            return str(resp)

        # --- Step 5: Ask for Name ---
        if state["step"] == "ask_name":
            if not speech_result:
                gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                gather.say('Please say your name.')
                resp.append(gather)
                return str(resp)
            # Save appointment
            dt = state.get("datetime", "TBD")
            service = state.get("service", "General")
            create_appointment(name=speech_result, phone=from_number, datetime=dt, service=service, notes="booked via AI")
            session_state[from_number] = {"step": "confirm", "service": service, "datetime": dt, "name": speech_result}
            gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
            gather.say(f'Thank you, {speech_result}. Your {service} appointment for {dt} is booked. Would you like a reminder before your appointment?')
            resp.append(gather)
            return str(resp)

        # --- Step 6: Offer Reminder & Confirmation Preference ---
        if state["step"] == "confirm":
            if speech_result and "yes" in speech_result.lower():
                gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                gather.say('Would you like to receive your reminder by SMS or email?')
                resp.append(gather)
                session_state[from_number]["step"] = "reminder_pref"
                return str(resp)
            else:
                resp.say('Thank you for calling! Your appointment is confirmed. Goodbye!')
                resp.hangup()
                session_state.pop(from_number, None)
                return str(resp)

        # --- Step 7: Reminder Preference ---
        if state["step"] == "reminder_pref":
            if speech_result and ("sms" in speech_result.lower() or "text" in speech_result.lower()):
                resp.say('A reminder will be sent by SMS before your appointment. Thank you for calling! Goodbye!')
            elif speech_result and "email" in speech_result.lower():
                resp.say('A reminder will be sent by email before your appointment. Thank you for calling! Goodbye!')
            else:
                resp.say('Thank you for calling! Your appointment is confirmed. Goodbye!')
            resp.hangup()
            session_state.pop(from_number, None)
            return str(resp)

        # --- Step 8: Feedback ---
        if state["step"] == "feedback":
            if speech_result and ("yes" in speech_result.lower() or "good" in speech_result.lower()):
                resp.say('Thank you for your feedback! Have a wonderful day!')
            else:
                resp.say('Thank you for calling! Goodbye!')
            resp.hangup()
            session_state.pop(from_number, None)
            return str(resp)

        # --- Fallback ---
        elif intent_label == "service":
            # Advanced Memory: Store rolling history for service path
            session_state[from_number] = session_state.get(from_number, {})
            history = session_state[from_number].get('history', [])
            history.append({
                'input': speech_result,
                'intent': intent_label,
                'sentiment': sentiment_label
            })
            if len(history) > 5:
                history = history[-5:]
            session_state[from_number]['history'] = history
            save_user_memory(from_number, history)
            memory_str = ''
            for h in history[:-1]:
                memory_str += f"User said: '{h['input']}' (intent: {h['intent']}, sentiment: {h['sentiment']}).\n"
            system_prompt = get_active_system_prompt()
            enhanced_prompt = f"""
{system_prompt}

The user intent is {intent_label}, and the user sentiment is {sentiment_label}. If the user seems negative or angry, soften your tone and show empathy. If the user is happy, sound more cheerful. Use simple, human-friendly words. Add polite conversational fillers like 'sure!', 'got it!', or 'let me check!' to make the tone more friendly. Break long answers into short sentences (ideally under 15 words) so the TTS sounds natural. Here is some context from earlier in the conversation: {memory_str} User: {speech_result} Assistant:"""
            ai_response = llama3_chat_completion(speech_result, system_prompt=enhanced_prompt)
            if not ai_response or 'Sorry, I could not process' in ai_response or len(ai_response.strip()) < 2:
                ai_response = "Hmm, I'm still learning that. Would you like me to search more?"
            import re
            def split_sentences(text):
                return [s.strip() for s in re.split(r'[.!?\n]|(?<=,)', text) if s.strip()]
            def add_filler(sentence, sentiment):
                if sentiment in ['negative', 'angry', 'sad']:
                    return "I'm here to help. " + sentence
                elif sentiment in ['positive', 'happy']:
                    return "Sure! " + sentence
                else:
                    return sentence
            sentences = split_sentences(ai_response)
            end_keywords = ['goodbye', 'bye', 'see you', 'exit', 'quit']
            if any(kw in speech_result.lower() for kw in end_keywords):
                for i, s in enumerate(sentences[:4]):
                    s = add_filler(s, sentiment_label)
                    resp.say(s)
                resp.hangup()
                session_state.pop(from_number, None)
                return str(resp)
            else:
                gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                for i, s in enumerate(sentences[:4]):
                    s = add_filler(s, sentiment_label)
                    gather.say(s)
                gather.say("If you have another question, please speak after the beep. Or say 'goodbye' to end the call.")
                resp.append(gather)
                session_state[from_number]["step"] = "intent"
                return str(resp)
        else:
            # Advanced Memory: Store rolling history for fallback path
            session_state[from_number] = session_state.get(from_number, {})
            history = session_state[from_number].get('history', [])
            history.append({
                'input': speech_result,
                'intent': intent_label,
                'sentiment': sentiment_label
            })
            if len(history) > 5:
                history = history[-5:]
            session_state[from_number]['history'] = history
            save_user_memory(from_number, history)
            memory_str = ''
            for h in history[:-1]:
                memory_str += f"User said: '{h['input']}' (intent: {h['intent']}, sentiment: {h['sentiment']}).\n"
            system_prompt = get_active_system_prompt()
            enhanced_prompt = f"""
{system_prompt}

The user intent is {intent_label}, and the user sentiment is {sentiment_label}. If the user seems negative or angry, soften your tone and show empathy. If the user is happy, sound more cheerful. Use simple, human-friendly words. Add polite conversational fillers like 'sure!', 'got it!', or 'let me check!' to make the tone more friendly. Break long answers into short sentences (ideally under 15 words) so the TTS sounds natural. Here is some context from earlier in the conversation: {memory_str} User: {speech_result} Assistant:"""
            ai_response = llama3_chat_completion(speech_result, system_prompt=enhanced_prompt)
            if not ai_response or 'Sorry, I could not process' in ai_response or len(ai_response.strip()) < 2:
                ai_response = "Hmm, I'm still learning that. Would you like me to search more?"
            import re
            def split_sentences(text):
                return [s.strip() for s in re.split(r'[.!?\n]|(?<=,)', text) if s.strip()]
            def add_filler(sentence, sentiment):
                if sentiment in ['negative', 'angry', 'sad']:
                    return "I'm here to help. " + sentence
                elif sentiment in ['positive', 'happy']:
                    return "Sure! " + sentence
                else:
                    return sentence
            sentences = split_sentences(ai_response)
            end_keywords = ['goodbye', 'bye', 'see you', 'exit', 'quit']
            if any(kw in speech_result.lower() for kw in end_keywords):
                for i, s in enumerate(sentences[:4]):
                    s = add_filler(s, sentiment_label)
                    resp.say(s)
                resp.hangup()
                session_state.pop(from_number, None)
                return str(resp)
            else:
                gather = Gather(input='speech', action='/twilio/webhook', method='POST', timeout=10)
                for i, s in enumerate(sentences[:4]):
                    s = add_filler(s, sentiment_label)
                    gather.say(s)
                gather.say("If you have another question, please speak after the beep. Or say 'goodbye' to end the call.")
                resp.append(gather)
                session_state[from_number]["step"] = "intent"
                return str(resp)
    except Exception as e:
        print("[Twilio Webhook Error]", e)
        resp.say('Sorry, an error occurred. Please try again later. Goodbye!')
        resp.hangup()
        return str(resp)

@app.post("/twilio/reminder-webhook", response_class=PlainTextResponse)
async def reminder_webhook(request: Request):
    """Handle outbound reminder calls"""
    form_data = await request.form()
    
    # Create a simple reminder message
    response = VoiceResponse()
    
    # Get appointment details from the call
    call_sid = form_data.get('CallSid', '')
    
    # Create a friendly reminder message
    reminder_text = """
    Hello! This is your appointment reminder. 
    You have an upcoming appointment scheduled. 
    Please call us back if you need to reschedule or have any questions. 
    Thank you for choosing our service!
    """
    
    # Use TTS to convert text to speech
    try:
        audio_url = coqui_tts(reminder_text)
        response.play(audio_url)
    except Exception as e:
        # Fallback to text-to-speech
        response.say(reminder_text, voice='alice')
    
    # Add a pause and hang up
    response.pause(length=2)
    response.hangup()
    
    return str(response)

@app.post("/twilio/status-callback")
async def status_callback(request: Request):
    """Handle call status updates"""
    form_data = await request.form()
    call_sid = form_data.get('CallSid', '')
    call_status = form_data.get('CallStatus', '')
    
    # Log the call status
    print(f"Call {call_sid} status: {call_status}")
    
    return {"status": "received"}

# --- Reminder API Endpoints ---
@app.post("/api/reminders/send/{appointment_id}")
async def send_reminder_call(appointment_id: int):
    """Send a reminder call for a specific appointment"""
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    c.execute('SELECT id, name, phone, datetime, service, notes FROM appointments WHERE id = ?', (appointment_id,))
    appointment = c.fetchone()
    conn.close()
    
    if not appointment:
        return {"error": "Appointment not found"}
    
    appointment_data = {
        'id': appointment[0],
        'name': appointment[1],
        'phone': appointment[2],
        'datetime': appointment[3],
        'service': appointment[4],
        'notes': appointment[5]
    }
    
    result = make_reminder_call(appointment_data['phone'], appointment_data)
    return result

@app.post("/api/reminders/send-all")
async def send_all_reminders():
    """Send reminder calls for all upcoming appointments"""
    upcoming_appointments = get_upcoming_appointments(hours_ahead=24)
    
    results = []
    for appointment in upcoming_appointments:
        result = make_reminder_call(appointment['phone'], appointment)
        results.append({
            'appointment_id': appointment['id'],
            'name': appointment['name'],
            'phone': appointment['phone'],
            'result': result
        })
    
    return {
        "total_appointments": len(upcoming_appointments),
        "results": results
    }

@app.get("/api/reminders/upcoming")
async def get_upcoming_reminders():
    """Get all upcoming appointments that need reminders"""
    appointments = get_upcoming_appointments(hours_ahead=24)
    return {"appointments": appointments}

@app.get("/appointments")
def list_appointments():
    from appointment_utils import get_appointments
    results = get_appointments()
    # Convert to dicts for JSON response
    appointments = [
        {
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "datetime": row[3],
            "service": row[4],
            "notes": row[5],
        }
        for row in results
    ]
    return {"appointments": appointments}

@app.post("/appointments")
def create_appointment_api(
    name: str = Body(...),
    phone: str = Body(...),
    datetime: str = Body(...),
    service: str = Body(""),
    notes: str = Body("")
):
    from appointment_utils import create_appointment
    # service is not used in the current DB schema, but included for future-proofing
    create_appointment(name, phone, datetime, notes)
    return {"status": "created"}

@app.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int, name: str = Body(None), phone: str = Body(None), datetime: str = Body(None), service: str = Body(None), notes: str = Body(None)):
    # Update logic (not present in appointment_utils, so implement inline)
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    # Only update provided fields
    fields = []
    values = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if phone is not None:
        fields.append("phone = ?")
        values.append(phone)
    if datetime is not None:
        fields.append("datetime = ?")
        values.append(datetime)
    if service is not None:
        fields.append("service = ?")
        values.append(service)
    if notes is not None:
        fields.append("notes = ?")
        values.append(notes)
    if not fields:
        return {"error": "No fields to update"}
    values.append(appointment_id)
    c.execute(f"UPDATE appointments SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.post("/ai/ask")
async def ai_ask(request: Request, data: dict = Body(...)):
    message = data.get("message", "")
    if not message:
        return JSONResponse({"response": "Please provide a message."}, status_code=400)
    # Use your LLM integration (llama3_chat_completion or similar)
    try:
        from hf_utils import llama3_chat_completion
        ai_response = llama3_chat_completion(message)
        if isinstance(ai_response, dict) and "error" in ai_response:
            return JSONResponse({"response": f"AI error: {ai_response['error']}"}, status_code=500)
        return {"response": ai_response if isinstance(ai_response, str) else str(ai_response)}
    except Exception as e:
        return JSONResponse({"response": f"Internal error: {e}"}, status_code=500)

@app.get("/ai", response_class=HTMLResponse)
def ai_chat_page(request: Request):
    return templates.TemplateResponse("ai.html", {"request": request}) 