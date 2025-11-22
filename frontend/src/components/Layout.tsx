import React, { ReactNode, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
  useMediaQuery,
  Avatar,
  Divider,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Event as EventIcon,
  Science as ScienceIcon,
  AdminPanelSettings as AdminIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
  ReportProblem as IncidentIcon,
  MedicalServices as ProvidersIcon,
  People as PatientsIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

const DRAWER_WIDTH = 260;

const allMenuItems = [
  { text: 'Chat', icon: <ChatIcon />, path: '/chat', color: '#840132', roles: ['patient'] },
  { text: 'Appointments', icon: <EventIcon />, path: '/appointments', color: '#000000', roles: ['patient', 'admin', 'staff'] },
  { text: 'Lab Tests', icon: <ScienceIcon />, path: '/labs', color: '#808080', roles: ['patient', 'admin', 'staff'] },
  { text: 'Providers', icon: <ProvidersIcon />, path: '/providers', color: '#840132', roles: ['admin', 'staff'] },
  { text: 'Patients', icon: <PatientsIcon />, path: '/patients', color: '#000000', roles: ['admin', 'staff'] },
  { text: 'Incidents', icon: <IncidentIcon />, path: '/incidents', color: '#808080', roles: ['admin', 'staff'] },
  { text: 'Admin', icon: <AdminIcon />, path: '/admin', color: '#840132', roles: ['admin'] },
];

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Get current user and filter menu items based on role
  const currentUser = api.getCurrentUser();
  const userRole = currentUser?.role || 'patient';
  
  // Debug logging
  console.log('Current user:', currentUser);
  console.log('User role:', userRole);
  
  const menuItems = allMenuItems.filter(item => item.roles.includes(userRole));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    api.logout();
    navigate('/login');
  };

  const handleMenuClick = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          px: 2.5,
          py: 2.5,
          background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)',
          boxShadow: '0 2px 8px rgba(132, 1, 50, 0.2)',
        }}
      >
        <Box
          component="img"
          src="/images/aub-logo.png"
          alt="AUB Logo"
          sx={{
            width: { xs: '100px', sm: '150px' },
            height: { xs: '37px', sm: '50px' },
            filter: 'brightness(0) invert(1)',
          }}
        />
        <Box>
          <Typography
            variant="h6"
            sx={{
              color: 'white',
              fontWeight: 700,
              fontSize: '1.2rem',
              lineHeight: 1.2,
              letterSpacing: '0.5px',
            }}
          >
            CareConnect
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255, 255, 255, 0.85)',
              fontSize: '0.7rem',
              fontWeight: 500,
              letterSpacing: '0.3px',
            }}
          >
            AUB Medical Center
          </Typography>
        </Box>
      </Toolbar>
      <Divider sx={{ borderColor: 'rgba(132, 1, 50, 0.12)' }} />
      <List sx={{ px: 1.5, py: 2, flexGrow: 1 }}>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={isSelected}
                onClick={() => handleMenuClick(item.path)}
                sx={{
                  borderRadius: 3,
                  py: 1.5,
                  px: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(132, 1, 50, 0.12)',
                    borderLeft: '4px solid #840132',
                    '&:hover': {
                      backgroundColor: 'rgba(132, 1, 50, 0.18)',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'rgba(132, 1, 50, 0.06)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isSelected ? '#840132' : '#808080',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isSelected ? 700 : 500,
                    fontSize: '0.95rem',
                    color: isSelected ? '#000000' : '#808080',
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      
      {/* User info at bottom */}
      <Divider sx={{ borderColor: 'rgba(132, 1, 50, 0.12)' }} />
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          background: 'linear-gradient(180deg, transparent 0%, rgba(132, 1, 50, 0.02) 100%)',
        }}
      >
        <Avatar
          sx={{
            width: 36,
            height: 36,
            bgcolor: '#840132',
            fontSize: '0.9rem',
            fontWeight: 600,
          }}
        >
          {currentUser?.name?.charAt(0).toUpperCase() || 'U'}
        </Avatar>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Typography
            variant="body2"
            sx={{
              fontWeight: 600,
              fontSize: '0.875rem',
              color: '#000000',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {currentUser?.name || 'User'}
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: '#808080',
              fontSize: '0.75rem',
              textTransform: 'capitalize',
            }}
          >
            {userRole}
          </Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
        <Box sx={{ display: 'flex', width: '100%', minHeight: '100vh', bgcolor: '#f5f7fa' }}>
      {/* Rest of JSX */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (theme: any) => theme.zIndex.drawer + 1,
          background: 'linear-gradient(90deg, #840132 0%, #5e0124 80%, #000000 100%)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 4px 16px rgba(132, 1, 50, 0.2)',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isMobile && (
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{
                  borderRadius: 0,
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.15)',
                  },
                }}
              >
                <MenuIcon />
              </IconButton>
            )}
            <Box
              component="img"
              src="/images/aub-logo.png"
              alt="AUB Logo"
              sx={{
                width: { xs: '100px', sm: '150px' },
                height: { xs: '37px', sm: '50px' },
                filter: 'brightness(0) invert(1)',
                display: { xs: 'none', sm: 'block' },
              }}
            />
            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{
                fontWeight: 700,
                fontSize: { xs: '1rem', sm: '1.25rem' },
                letterSpacing: '0.5px',
                background: 'linear-gradient(90deg, #ffffff 0%, rgba(255,255,255,0.9) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              {isMobile ? 'CareConnect' : 'CareConnect - Smart Health Assistant'}
            </Typography>
          </Box>
          <IconButton
            color="inherit"
            onClick={handleProfileMenuOpen}
            sx={{
              borderRadius: 0,
              transition: 'all 0.2s ease',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                transform: 'scale(1.05)',
              },
            }}
          >
            <Avatar
              sx={{
                width: 36,
                height: 36,
                bgcolor: 'rgba(255, 255, 255, 0.25)',
                fontSize: '1rem',
                fontWeight: 700,
                border: '2px solid rgba(255, 255, 255, 0.3)',
              }}
            >
              {currentUser?.name?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                mt: 1.5,
                minWidth: 220,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
              },
            }}
          >
            <Box sx={{ px: 2.5, py: 2, borderBottom: '1px solid rgba(0,0,0,0.08)' }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                {currentUser?.name || 'User'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8125rem' }}>
                {currentUser?.email}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  mt: 0.5,
                  px: 1,
                  py: 0.25,
                  borderRadius: 1,
                  bgcolor: 'rgba(132, 1, 50, 0.1)',
                  color: '#840132',
                  textTransform: 'capitalize',
                  fontWeight: 600,
                  display: 'inline-block',
                }}
              >
                {userRole}
              </Typography>
            </Box>
            <MenuItem
              onClick={handleLogout}
              sx={{
                py: 1.5,
                px: 2.5,
                mt: 1,
                mx: 1,
                mb: 1,
                borderRadius: 2,
                color: '#d32f2f',
                fontWeight: 600,
                '&:hover': {
                  backgroundColor: 'rgba(211, 47, 47, 0.08)',
                },
              }}
            >
              <ListItemIcon sx={{ color: '#d32f2f' }}>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Desktop Drawer */}
      {!isMobile && (
        <Drawer
          variant="permanent"
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              borderRight: '1px solid rgba(132, 1, 50, 0.08)',
              boxShadow: '4px 0 12px rgba(0, 0, 0, 0.05)',
            },
          }}
        >
          {drawer}
        </Drawer>
      )}

      {/* Mobile Drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              boxShadow: '8px 0 24px rgba(0, 0, 0, 0.15)',
            },
          }}
        >
          {drawer}
        </Drawer>
      )}

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, sm: 3, md: 4 },
          width: { xs: '100%', md: `calc(100% - ${DRAWER_WIDTH}px)` },
          minHeight: '100vh',
          bgcolor: '#f5f7fa',
          backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(132, 1, 50, 0.03) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(0, 90, 67, 0.02) 0%, transparent 50%)',
        }}
      >
        <Toolbar />
        <Box sx={{ mt: { xs: 2, sm: 3 } }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
