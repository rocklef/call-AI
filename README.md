# Appointment Management System

A comprehensive appointment management system with AI-powered features including voice interaction, multilingual support, and automated reminders.

## Features

- **Appointment Management**: Create, view, and manage appointments
- **AI Voice Assistant**: Voice-based interaction using speech recognition and text-to-speech
- **Multilingual Support**: Native support for multiple languages
- **Automated Reminders**: Smart reminder system for appointments
- **Admin Dashboard**: Comprehensive admin interface for managing the system
- **Frontend Interface**: Modern React-based user interface

## Project Structure

```
sy/
├── main.py                 # Main application entry point
├── appointment_utils.py    # Appointment management utilities
├── tts_utils.py          # Text-to-speech utilities
├── whisper_utils.py      # Speech recognition utilities
├── hf_utils.py           # Hugging Face model utilities
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
├── frontend/            # React frontend
└── frontend-vite/       # Vite-based frontend
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rocklef/call-AI.git
   cd call-AI
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Set up frontend (optional)**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## Usage

1. Start the application using `python main.py`
2. Access the web interface at `http://localhost:5000`
3. Use voice commands or the web interface to manage appointments
4. Access admin features at `/admin` routes

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository.