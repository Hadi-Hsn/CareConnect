import React, { ReactNode, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
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
  Menu,
  MenuItem,
  alpha,
  Tooltip,
  Badge,
} from "@mui/material";
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
  LocalHospital as DirectoryIcon,
  KeyboardArrowRight as ArrowIcon,
  CalendarMonth as CalendarIcon,
  Assignment as ResultsIcon,
} from "@mui/icons-material";
import { api } from "@/lib/api";

const DRAWER_WIDTH = 280;

const allMenuItems = [
  {
    text: "AI Assistant",
    icon: <ChatIcon />,
    path: "/chat",
    color: "#840132",
    roles: ["patient"],
    description: "Chat with our AI",
  },
  {
    text: "My Appointments",
    icon: <EventIcon />,
    path: "/appointments",
    color: "#2e7d32",
    roles: ["patient"],
    description: "View your bookings",
  },
  {
    text: "My Test Results",
    icon: <ResultsIcon />,
    path: "/test-results",
    color: "#9c27b0",
    roles: ["patient"],
    description: "View your results",
  },
  {
    text: "Calendar",
    icon: <CalendarIcon />,
    path: "/calendar",
    color: "#1976d2",
    roles: ["patient", "admin", "staff"],
    description: "View calendar",
  },
  {
    text: "Lab Tests",
    icon: <ScienceIcon />,
    path: "/labs",
    color: "#1565c0",
    roles: ["patient"],
    description: "Browse available tests",
  },
  {
    text: "Find Providers",
    icon: <DirectoryIcon />,
    path: "/find-providers",
    color: "#7b1fa2",
    roles: ["patient"],
    description: "Search doctors",
  },
  {
    text: "Appointments",
    icon: <EventIcon />,
    path: "/appointments",
    color: "#2e7d32",
    roles: ["admin", "staff"],
    description: "Manage all appointments",
  },
  {
    text: "Lab Catalog",
    icon: <ScienceIcon />,
    path: "/labs",
    color: "#1565c0",
    roles: ["admin", "staff"],
    description: "Manage lab tests",
  },
  {
    text: "Manage Providers",
    icon: <ProvidersIcon />,
    path: "/providers",
    color: "#ed6c02",
    roles: ["admin", "staff"],
    description: "Provider management",
  },
  {
    text: "Patients",
    icon: <PatientsIcon />,
    path: "/patients",
    color: "#0288d1",
    roles: ["admin", "staff"],
    description: "Patient records",
  },
  {
    text: "Incidents",
    icon: <IncidentIcon />,
    path: "/incidents",
    color: "#d32f2f",
    roles: ["admin", "staff"],
    description: "View incidents",
  },
  {
    text: "Admin Panel",
    icon: <AdminIcon />,
    path: "/admin",
    color: "#840132",
    roles: ["admin"],
    description: "System settings",
  },
];

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Get current user and filter menu items based on role
  const currentUser = api.getCurrentUser();
  const userRole = currentUser?.role || "patient";

  const menuItems = allMenuItems.filter((item) =>
    item.roles.includes(userRole),
  );

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    api.logout();
    navigate("/login");
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
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "#fafbfc",
      }}
    >
      {/* Navigation */}
      <Box sx={{ px: 2, py: 4, flexGrow: 1, overflowY: "auto" }}>
        <Typography
          variant="overline"
          sx={{
            px: 2,
            fontSize: "0.65rem",
            fontWeight: 700,
            color: "text.disabled",
            letterSpacing: "1px",
          }}
        >
          Navigation
        </Typography>
        <List sx={{ mt: 1 }}>
          {menuItems.map((item) => {
            const isSelected = location.pathname === item.path;
            return (
              <ListItem
                key={item.text + item.path}
                disablePadding
                sx={{ mb: 0.5 }}
              >
                <Tooltip title={item.description} placement="right" arrow>
                  <ListItemButton
                    selected={isSelected}
                    onClick={() => handleMenuClick(item.path)}
                    sx={{
                      borderRadius: 2.5,
                      py: 1.5,
                      px: 2,
                      transition: "all 0.2s ease",
                      position: "relative",
                      overflow: "hidden",
                      "&.Mui-selected": {
                        background: `linear-gradient(135deg, ${alpha(item.color, 0.12)} 0%, ${alpha(item.color, 0.06)} 100%)`,
                        "&::before": {
                          content: '""',
                          position: "absolute",
                          left: 0,
                          top: "50%",
                          transform: "translateY(-50%)",
                          width: 4,
                          height: "60%",
                          borderRadius: "0 4px 4px 0",
                          bgcolor: item.color,
                        },
                        "&:hover": {
                          background: `linear-gradient(135deg, ${alpha(item.color, 0.18)} 0%, ${alpha(item.color, 0.1)} 100%)`,
                        },
                      },
                      "&:hover": {
                        background: alpha(item.color, 0.06),
                        transform: "translateX(4px)",
                      },
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 44,
                        color: isSelected ? item.color : "text.secondary",
                        transition: "color 0.2s ease",
                      }}
                    >
                      <Box
                        sx={{
                          width: 36,
                          height: 36,
                          borderRadius: 2,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          bgcolor: isSelected
                            ? alpha(item.color, 0.15)
                            : "transparent",
                          transition: "all 0.2s ease",
                        }}
                      >
                        {item.icon}
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={item.text}
                      primaryTypographyProps={{
                        fontWeight: isSelected ? 700 : 500,
                        fontSize: "0.9rem",
                        color: isSelected ? "text.primary" : "text.secondary",
                      }}
                    />
                    {isSelected && (
                      <ArrowIcon sx={{ color: item.color, fontSize: 18 }} />
                    )}
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            );
          })}
        </List>
      </Box>

      {/* User Card */}
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            p: 2,
            borderRadius: 3,
            background: "linear-gradient(135deg, #fff 0%, #f8f9fa 100%)",
            border: "1px solid",
            borderColor: "divider",
            boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
            <Badge
              overlap="circular"
              anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
              badgeContent={
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    bgcolor: "#4caf50",
                    border: "2px solid white",
                  }}
                />
              }
            >
              <Avatar
                sx={{
                  width: 44,
                  height: 44,
                  background:
                    "linear-gradient(135deg, #840132 0%, #5e0124 100%)",
                  fontSize: "1rem",
                  fontWeight: 700,
                  boxShadow: "0 4px 12px rgba(132, 1, 50, 0.3)",
                }}
              >
                {currentUser?.name?.charAt(0).toUpperCase() || "U"}
              </Avatar>
            </Badge>
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 700,
                  fontSize: "0.9rem",
                  color: "text.primary",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {currentUser?.name || "User"}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: "text.secondary",
                  fontSize: "0.75rem",
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                }}
              >
                <Box
                  component="span"
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    bgcolor:
                      userRole === "admin"
                        ? "#840132"
                        : userRole === "staff"
                          ? "#1976d2"
                          : "#4caf50",
                  }}
                />
                {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
              </Typography>
            </Box>
            <Tooltip title="Sign out">
              <IconButton
                size="small"
                onClick={handleLogout}
                sx={{
                  color: "text.secondary",
                  "&:hover": {
                    color: "#d32f2f",
                    bgcolor: alpha("#d32f2f", 0.1),
                  },
                }}
              >
                <LogoutIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box
      sx={{
        display: "flex",
        width: "100%",
        minHeight: "100vh",
        bgcolor: "#f5f7fa",
      }}
    >
      {/* Rest of JSX */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (theme: any) => theme.zIndex.drawer + 1,
          bgcolor: "#fff",
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            {isMobile && (
              <IconButton
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{
                  color: "#840132",
                  "&:hover": {
                    backgroundColor: alpha("#840132", 0.08),
                  },
                }}
              >
                <MenuIcon />
              </IconButton>
            )}
            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{
                fontWeight: 700,
                fontSize: { xs: "1rem", sm: "1.15rem" },
                color: "#840132",
              }}
            >
              {isMobile ? "CareConnect" : "CareConnect"}
            </Typography>
            {!isMobile && (
              <Typography
                variant="body2"
                sx={{
                  color: "text.secondary",
                  fontWeight: 400,
                  borderLeft: "1px solid",
                  borderColor: "divider",
                  pl: 2,
                  ml: 1,
                }}
              >
                Smart Health Assistant
              </Typography>
            )}
          </Box>
          <IconButton
            onClick={handleProfileMenuOpen}
            sx={{
              transition: "all 0.2s ease",
              "&:hover": {
                backgroundColor: alpha("#840132", 0.08),
              },
            }}
          >
            <Avatar
              sx={{
                width: 38,
                height: 38,
                bgcolor: alpha("#840132", 0.1),
                color: "#840132",
                fontSize: "1rem",
                fontWeight: 700,
              }}
            >
              {currentUser?.name?.charAt(0).toUpperCase() || "U"}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "right",
            }}
            transformOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
            PaperProps={{
              sx: {
                mt: 1.5,
                minWidth: 220,
                borderRadius: 3,
                boxShadow: "0 8px 32px rgba(0, 0, 0, 0.15)",
              },
            }}
          >
            <Box
              sx={{
                px: 2.5,
                py: 2,
                borderBottom: "1px solid rgba(0,0,0,0.08)",
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                {currentUser?.name || "User"}
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ fontSize: "0.8125rem" }}
              >
                {currentUser?.email}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  mt: 0.5,
                  px: 1,
                  py: 0.25,
                  borderRadius: 1,
                  bgcolor: "rgba(132, 1, 50, 0.1)",
                  color: "#840132",
                  textTransform: "capitalize",
                  fontWeight: 600,
                  display: "inline-block",
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
                color: "#d32f2f",
                fontWeight: 600,
                "&:hover": {
                  backgroundColor: "rgba(211, 47, 47, 0.08)",
                },
              }}
            >
              <ListItemIcon sx={{ color: "#d32f2f" }}>
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
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              boxSizing: "border-box",
              borderRight: "1px solid rgba(132, 1, 50, 0.08)",
              boxShadow: "4px 0 12px rgba(0, 0, 0, 0.05)",
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
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              boxSizing: "border-box",
              boxShadow: "8px 0 24px rgba(0, 0, 0, 0.15)",
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
          width: { xs: "100%", md: `calc(100% - ${DRAWER_WIDTH}px)` },
          minHeight: "100vh",
          bgcolor: "#f5f7fa",
          backgroundImage:
            "radial-gradient(circle at 20% 50%, rgba(132, 1, 50, 0.03) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(0, 90, 67, 0.02) 0%, transparent 50%)",
        }}
      >
        <Toolbar />
        <Box sx={{ mt: { xs: 2, sm: 3 } }}>{children}</Box>
      </Box>
    </Box>
  );
}
