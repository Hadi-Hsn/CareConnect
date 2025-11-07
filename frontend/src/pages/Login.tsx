import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  TextField,
  Typography,
  Tab,
  Tabs,
  Alert,
  useTheme,
  useMediaQuery,
  Divider,
  Link,
} from '@mui/material';
import {
  LocalHospital as HospitalIcon,
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function LoginPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [tabValue, setTabValue] = useState(0);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.login(email, password);
      // Force a page reload to update authentication state
      window.location.href = '/chat';
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    // Validate password length
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    
    setLoading(true);
    try {
      await api.register(email, name, password, confirmPassword, phone);
      // Force a page reload to update authentication state
      window.location.href = '/chat';
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (userEmail: string, userPassword: string) => {
    setError('');
    setLoading(true);
    try {
      await api.login(userEmail, userPassword);
      // Force a page reload to update authentication state
      window.location.href = '/chat';
    } catch (err) {
      setError('Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #840132 0%, #5e0124 50%, #000000 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: { xs: 3, sm: 4 },
        px: { xs: 2, sm: 3 },
      }}
    >
      <Container maxWidth="sm">
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {/* Logo and Title */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              mb: 2,
            }}
          >
            <HospitalIcon
              sx={{
                fontSize: { xs: 48, sm: 64 },
                color: 'white',
              }}
            />
            <Typography
              component="h1"
              variant="h2"
              sx={{
                color: 'white',
                fontWeight: 700,
                fontSize: { xs: '2rem', sm: '2.5rem' },
              }}
            >
              CareConnect
            </Typography>
          </Box>

          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              textAlign: 'center',
              mb: 1,
              fontSize: { xs: '1rem', sm: '1.25rem' },
            }}
          >
            AUB Medical Center
          </Typography>

          <Typography
            variant="body1"
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              textAlign: 'center',
              mb: 4,
              fontSize: { xs: '0.875rem', sm: '1rem' },
            }}
          >
            Your Smart Health Assistant
          </Typography>

          {/* Main Card */}
          <Card
            sx={{
              width: '100%',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
              borderRadius: { xs: 2, sm: 3 },
            }}
          >
            <CardContent sx={{ p: { xs: 2, sm: 4 } }}>
              <Tabs
                value={tabValue}
                onChange={(_, v) => {
                  setTabValue(v);
                  setError('');
                }}
                variant="fullWidth"
                sx={{
                  mb: 2,
                  '& .MuiTab-root': {
                    fontWeight: 600,
                    fontSize: { xs: '0.875rem', sm: '1rem' },
                  },
                  '& .Mui-selected': {
                    color: theme.palette.primary.main,
                  },
                }}
              >
                <Tab icon={<LoginIcon />} iconPosition="start" label="Login" />
                <Tab icon={<RegisterIcon />} iconPosition="start" label="Register" />
              </Tabs>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <TabPanel value={tabValue} index={0}>
                <form onSubmit={handleLogin}>
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    label="Email Address"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                    autoComplete="email"
                    size={isMobile ? 'small' : 'medium'}
                  />
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    autoComplete="current-password"
                    size={isMobile ? 'small' : 'medium'}
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size={isMobile ? 'medium' : 'large'}
                    disabled={loading}
                    sx={{
                      mt: 3,
                      mb: 2,
                      py: { xs: 1.5, sm: 2 },
                      fontSize: { xs: '0.875rem', sm: '1rem' },
                    }}
                  >
                    {loading ? 'Logging in...' : 'Login'}
                  </Button>
                  <Box sx={{ textAlign: 'center' }}>
                    <Link
                      component="button"
                      variant="body2"
                      onClick={() => {}}
                      sx={{ color: theme.palette.primary.main }}
                    >
                      Forgot password?
                    </Link>
                  </Box>
                </form>

                <Divider sx={{ my: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    Demo Accounts
                  </Typography>
                </Divider>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  <Button
                    variant="outlined"
                    size={isMobile ? 'small' : 'medium'}
                    fullWidth
                    onClick={() => handleDemoLogin('hadihacan@gmail.com', 'password123')}
                    disabled={loading}
                    sx={{ justifyContent: 'flex-start', px: 2 }}
                  >
                    <Box sx={{ textAlign: 'left', width: '100%' }}>
                      <Typography variant="body2" fontWeight={600}>
                        Patient Demo
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        hadihacan@gmail.com
                      </Typography>
                    </Box>
                  </Button>
                  <Button
                    variant="outlined"
                    size={isMobile ? 'small' : 'medium'}
                    fullWidth
                    onClick={() => handleDemoLogin('hadi.wmail@gmail.com', 'admin123')}
                    disabled={loading}
                    sx={{ justifyContent: 'flex-start', px: 2 }}
                  >
                    <Box sx={{ textAlign: 'left', width: '100%' }}>
                      <Typography variant="body2" fontWeight={600}>
                        Admin Demo
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        hadi.wmail@gmail.com
                      </Typography>
                    </Box>
                  </Button>
                </Box>
              </TabPanel>

              <TabPanel value={tabValue} index={1}>
                <form onSubmit={handleRegister}>
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    label="Full Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={loading}
                    autoComplete="name"
                    size={isMobile ? 'small' : 'medium'}
                  />
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    label="Email Address"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                    autoComplete="email"
                    size={isMobile ? 'small' : 'medium'}
                  />
                  <TextField
                    margin="normal"
                    fullWidth
                    label="Phone Number"
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    disabled={loading}
                    autoComplete="tel"
                    placeholder="+961 1 234 5678"
                    helperText="Optional - for appointment reminders"
                    size={isMobile ? 'small' : 'medium'}
                  />
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    autoComplete="new-password"
                    helperText="Minimum 8 characters"
                    size={isMobile ? 'small' : 'medium'}
                  />
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    label="Confirm Password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                    autoComplete="new-password"
                    error={confirmPassword !== '' && password !== confirmPassword}
                    helperText={
                      confirmPassword !== '' && password !== confirmPassword
                        ? 'Passwords do not match'
                        : ''
                    }
                    size={isMobile ? 'small' : 'medium'}
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size={isMobile ? 'medium' : 'large'}
                    disabled={loading}
                    sx={{
                      mt: 3,
                      py: { xs: 1.5, sm: 2 },
                      fontSize: { xs: '0.875rem', sm: '1rem' },
                    }}
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                  </Button>
                </form>
              </TabPanel>
            </CardContent>
          </Card>

          {/* Footer */}
          <Typography
            variant="body2"
            sx={{
              color: 'rgba(255, 255, 255, 0.6)',
              textAlign: 'center',
              mt: 3,
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
            }}
          >
            © 2025 American University of Beirut Medical Center
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}
