import * as React from 'react';
import {
  Box,
  CssBaseline,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Card,
  CardContent,
  Button,
  Grid,
  Avatar,
  Chip,
  LinearProgress,
  IconButton,
  Badge
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import EventIcon from '@mui/icons-material/Event';
import BarChartIcon from '@mui/icons-material/BarChart';
import SettingsIcon from '@mui/icons-material/Settings';
import NotificationsIcon from '@mui/icons-material/Notifications';
import PersonIcon from '@mui/icons-material/Person';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ScheduleIcon from '@mui/icons-material/Schedule';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

const drawerWidth = 280;

function DashboardContent() {
  return (
    <Box sx={{
      flexGrow: 1,
      p: 4,
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh'
    }}>
      <Toolbar />

      {/* Welcome Section */}
      <Box sx={{ mb: 4, color: 'white' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold', mb: 1 }}>
          Welcome back, Sarah! 👋
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9 }}>
          Here's what's happening with your appointments today
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            transition: 'transform 0.3s ease-in-out',
            '&:hover': { transform: 'translateY(-5px)' }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{
                  bgcolor: '#4CAF50',
                  mr: 2,
                  width: 56,
                  height: 56
                }}>
                  <EventIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#2E7D32' }}>
                    12
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Today's Appointments
                  </Typography>
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={75}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: '#E8F5E8',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: '#4CAF50'
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            transition: 'transform 0.3s ease-in-out',
            '&:hover': { transform: 'translateY(-5px)' }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{
                  bgcolor: '#2196F3',
                  mr: 2,
                  width: 56,
                  height: 56
                }}>
                  <CheckCircleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1976D2' }}>
                    8
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Completed Today
                  </Typography>
                </Box>
              </Box>
              <Chip
                label="+15% from yesterday"
                size="small"
                color="primary"
                sx={{ fontSize: '0.75rem' }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            transition: 'transform 0.3s ease-in-out',
            '&:hover': { transform: 'translateY(-5px)' }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{
                  bgcolor: '#FF9800',
                  mr: 2,
                  width: 56,
                  height: 56
                }}>
                  <ScheduleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#F57C00' }}>
                    4
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending
                  </Typography>
                </Box>
              </Box>
              <Chip
                label="2 urgent"
                size="small"
                color="warning"
                icon={<WarningIcon />}
                sx={{ fontSize: '0.75rem' }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            transition: 'transform 0.3s ease-in-out',
            '&:hover': { transform: 'translateY(-5px)' }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{
                  bgcolor: '#9C27B0',
                  mr: 2,
                  width: 56,
                  height: 56
                }}>
                  <TrendingUpIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#7B1FA2' }}>
                    92%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Satisfaction Rate
                  </Typography>
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={92}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: '#F3E5F5',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: '#9C27B0'
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Cards */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            height: 400
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                Recent Appointments
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {[
                  { name: 'Dr. Johnson', time: '09:00 AM', status: 'Completed', color: '#4CAF50' },
                  { name: 'Dr. Smith', time: '10:30 AM', status: 'In Progress', color: '#2196F3' },
                  { name: 'Dr. Williams', time: '02:00 PM', status: 'Upcoming', color: '#FF9800' },
                  { name: 'Dr. Brown', time: '04:15 PM', status: 'Upcoming', color: '#FF9800' }
                ].map((appointment, index) => (
                  <Box key={index} sx={{
                    display: 'flex',
                    alignItems: 'center',
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'rgba(0,0,0,0.02)',
                    border: '1px solid rgba(0,0,0,0.05)'
                  }}>
                    <Avatar sx={{ mr: 2, bgcolor: appointment.color }}>
                      <PersonIcon />
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {appointment.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {appointment.time}
                      </Typography>
                    </Box>
                    <Chip
                      label={appointment.status}
                      size="small"
                      sx={{
                        bgcolor: appointment.color,
                        color: 'white',
                        fontWeight: 'bold'
                      }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            height: 400
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  fullWidth
                  sx={{
                    py: 2,
                    background: 'linear-gradient(45deg, #4CAF50 30%, #66BB6A 90%)',
                    borderRadius: 2,
                    fontWeight: 'bold',
                    textTransform: 'none',
                    fontSize: '1rem'
                  }}
                >
                  Book New Appointment
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{
                    py: 2,
                    borderRadius: 2,
                    fontWeight: 'bold',
                    textTransform: 'none',
                    fontSize: '1rem',
                    borderColor: '#2196F3',
                    color: '#2196F3',
                    '&:hover': {
                      borderColor: '#1976D2',
                      bgcolor: 'rgba(33, 150, 243, 0.04)'
                    }
                  }}
                >
                  View Calendar
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{
                    py: 2,
                    borderRadius: 2,
                    fontWeight: 'bold',
                    textTransform: 'none',
                    fontSize: '1rem',
                    borderColor: '#FF9800',
                    color: '#FF9800',
                    '&:hover': {
                      borderColor: '#F57C00',
                      bgcolor: 'rgba(255, 152, 0, 0.04)'
                    }
                  }}
                >
                  Export Reports
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 2px 20px rgba(0,0,0,0.1)'
        }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{
            flexGrow: 1,
            fontWeight: 'bold',
            background: 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            🏥 Smart Appointment Dashboard
          </Typography>
          <IconButton sx={{ mr: 2 }}>
            <Badge badgeContent={4} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          <Avatar sx={{ bgcolor: '#667eea' }}>
            <PersonIcon />
          </Avatar>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: 'border-box',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRight: '1px solid rgba(0,0,0,0.1)'
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', p: 2 }}>
          <List>
            <ListItem button key="Dashboard" sx={{
              mb: 1,
              borderRadius: 2,
              bgcolor: 'rgba(102, 126, 234, 0.1)',
              '&:hover': {
                bgcolor: 'rgba(102, 126, 234, 0.2)'
              }
            }}>
              <ListItemIcon sx={{ color: '#667eea' }}>
                <DashboardIcon />
              </ListItemIcon>
              <ListItemText
                primary="Dashboard"
                sx={{
                  '& .MuiListItemText-primary': {
                    fontWeight: 'bold',
                    color: '#667eea'
                  }
                }}
              />
            </ListItem>
            <ListItem button key="Appointments" sx={{
              mb: 1,
              borderRadius: 2,
              '&:hover': {
                bgcolor: 'rgba(0,0,0,0.04)'
              }
            }}>
              <ListItemIcon>
                <EventIcon />
              </ListItemIcon>
              <ListItemText primary="Appointments" />
            </ListItem>
            <ListItem button key="Analytics" sx={{
              mb: 1,
              borderRadius: 2,
              '&:hover': {
                bgcolor: 'rgba(0,0,0,0.04)'
              }
            }}>
              <ListItemIcon>
                <BarChartIcon />
              </ListItemIcon>
              <ListItemText primary="Analytics" />
            </ListItem>
            <ListItem button key="Settings" sx={{
              mb: 1,
              borderRadius: 2,
              '&:hover': {
                bgcolor: 'rgba(0,0,0,0.04)'
              }
            }}>
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItem>
          </List>
          <Divider sx={{ my: 2 }} />
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1 }}>
        <DashboardContent />
      </Box>
    </Box>
  );
}

export default App;
