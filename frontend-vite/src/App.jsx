import * as React from 'react';
import { Box, CssBaseline, Drawer, AppBar, Toolbar, Typography, List, ListItem, ListItemIcon, ListItemText, Divider, Card, CardContent, Button, Grid } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import EventIcon from '@mui/icons-material/Event';
import BarChartIcon from '@mui/icons-material/BarChart';
import SettingsIcon from '@mui/icons-material/Settings';

const drawerWidth = 220;

function DashboardContent() {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Toolbar />
      <Typography variant="h4" gutterBottom>
        Welcome to Your Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Upcoming Appointments</Typography>
              <Typography variant="body2" color="text.secondary">
                You have 3 appointments today.
              </Typography>
              <Button variant="contained" sx={{ mt: 2 }}>View All</Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Statistics</Typography>
              <Typography variant="body2" color="text.secondary">
                12 appointments this week
              </Typography>
              <Button variant="outlined" sx={{ mt: 2 }}>See Details</Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Quick Actions</Typography>
              <Button variant="contained" color="primary" sx={{ mt: 1, mr: 1 }}>Book Appointment</Button>
              <Button variant="outlined" color="secondary" sx={{ mt: 1 }}>Export Data</Button>
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
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            Interactive Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <ListItem button key="Dashboard">
              <ListItemIcon><DashboardIcon /></ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem button key="Appointments">
              <ListItemIcon><EventIcon /></ListItemIcon>
              <ListItemText primary="Appointments" />
            </ListItem>
            <ListItem button key="Analytics">
              <ListItemIcon><BarChartIcon /></ListItemIcon>
              <ListItemText primary="Analytics" />
            </ListItem>
            <ListItem button key="Settings">
              <ListItemIcon><SettingsIcon /></ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItem>
          </List>
          <Divider />
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
        <DashboardContent />
      </Box>
    </Box>
  );
}

export default App; 