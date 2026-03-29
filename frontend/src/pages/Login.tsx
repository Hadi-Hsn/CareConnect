import React, { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Tab,
  Tabs,
  Alert,
  useTheme,
  useMediaQuery,
  Link,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Grid,
} from "@mui/material";
import {
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
} from "@mui/icons-material";
import { api } from "@/lib/api";

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

// Common country codes with names
const COUNTRY_CODES = [
  { code: "+1", name: "USA/Canada" },
  { code: "+44", name: "United Kingdom" },
  { code: "+961", name: "Lebanon" },
  { code: "+971", name: "UAE" },
  { code: "+966", name: "Saudi Arabia" },
  { code: "+20", name: "Egypt" },
  { code: "+962", name: "Jordan" },
  { code: "+91", name: "India" },
  { code: "+86", name: "China" },
  { code: "+33", name: "France" },
  { code: "+49", name: "Germany" },
  { code: "+39", name: "Italy" },
  { code: "+34", name: "Spain" },
  { code: "+81", name: "Japan" },
  { code: "+82", name: "South Korea" },
];

export default function LoginPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [tabValue, setTabValue] = useState(0);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [countryCode, setCountryCode] = useState("+961");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.login(email, password);
      // Force a page reload to update authentication state
      window.location.href = "/chat";
    } catch (err: any) {
      console.error("Login error:", err);

      // Handle different types of errors
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        // Handle array of validation errors (Pydantic format)
        if (Array.isArray(detail)) {
          const errorMessages = detail
            .map((error: any) => {
              const field = error.loc?.[1] || error.loc?.[0] || "field";
              return `${field}: ${error.msg}`;
            })
            .join(", ");
          setError(errorMessages);
        } else if (typeof detail === "string") {
          setError(detail);
        } else {
          setError("Invalid email or password");
        }
      } else if (err.response?.status === 401) {
        setError("Invalid email or password");
      } else if (err.response?.status === 429) {
        setError("Too many login attempts. Please try again later.");
      } else if (err.message) {
        setError(err.message);
      } else {
        setError("Login failed. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate passwords match
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Validate password length
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    // Validate phone number is provided
    if (!phone || phone.trim() === "") {
      setError("Phone number is required");
      return;
    }

    // Validate phone number length
    const trimmedPhone = phone.trim();
    if (trimmedPhone.length < 7) {
      setError("Phone number must be at least 7 digits long");
      return;
    }

    // Check that it has at least 7 digits
    const digitsOnly = trimmedPhone.replace(/\D/g, "");
    if (digitsOnly.length < 7) {
      setError("Phone number must contain at least 7 digits");
      return;
    }

    setLoading(true);
    try {
      await api.register(
        email,
        name,
        password,
        confirmPassword,
        phone,
        countryCode,
      );
      // Force a page reload to update authentication state
      window.location.href = "/chat";
    } catch (err: any) {
      console.error("Registration error:", err);

      // Handle different types of errors
      if (err.response?.data?.detail) {
        // Backend validation error
        const detail = err.response.data.detail;

        // Handle array of validation errors (Pydantic format)
        if (Array.isArray(detail)) {
          const errorMessages = detail
            .map((error: any) => {
              const field = error.loc?.[1] || error.loc?.[0] || "field";
              return `${field}: ${error.msg}`;
            })
            .join(", ");
          setError(errorMessages);
        } else if (typeof detail === "string") {
          // Simple string error message
          setError(detail);
        } else {
          setError(
            "Registration failed. Please check your inputs and try again.",
          );
        }
      } else if (err.response?.status === 400) {
        setError("Invalid registration data. Please check all fields.");
      } else if (err.response?.status === 409) {
        setError("An account with this email or phone number already exists.");
      } else if (err.message) {
        setError(err.message);
      } else {
        setError("Registration failed. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        width: "100%",
        background:
          "linear-gradient(135deg, #840132 0%, #5e0124 40%, #000000 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        py: { xs: 3, sm: 4 },
        px: { xs: 2, sm: 3 },
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background:
            "radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 70%, rgba(0, 90, 67, 0.15) 0%, transparent 50%)",
          pointerEvents: "none",
        },
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: "500px",
          position: "relative",
          zIndex: 1,
          px: { xs: 2, sm: 3 },
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          {/* Logo and Title */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 2.5,
              mb: 2,
              animation: "fadeInDown 0.6s ease-out",
              "@keyframes fadeInDown": {
                "0%": { opacity: 0, transform: "translateY(-30px)" },
                "100%": { opacity: 1, transform: "translateY(0)" },
              },
            }}
          >
            <Typography
              component="h1"
              variant="h2"
              sx={{
                color: "white",
                fontWeight: 800,
                fontSize: { xs: "2.25rem", sm: "3rem" },
                textShadow: "0 4px 16px rgba(0, 0, 0, 0.4)",
                letterSpacing: "1px",
              }}
            >
              CareConnect
            </Typography>
          </Box>

          <Typography
            variant="h6"
            sx={{
              color: "rgba(255, 255, 255, 0.95)",
              textAlign: "center",
              mb: 1,
              fontSize: { xs: "1.125rem", sm: "1.375rem" },
              fontWeight: 600,
              textShadow: "0 2px 8px rgba(0, 0, 0, 0.3)",
            }}
          >
            Smart Health Assistant
          </Typography>

          <Typography
            variant="body1"
            sx={{
              color: "rgba(255, 255, 255, 0.8)",
              textAlign: "center",
              mb: 4,
              fontSize: { xs: "0.9375rem", sm: "1.0625rem" },
              fontWeight: 500,
              animation: "fadeIn 0.8s ease-out 0.3s both",
              "@keyframes fadeIn": {
                "0%": { opacity: 0 },
                "100%": { opacity: 1 },
              },
            }}
          >
            Your Smart Health Assistant
          </Typography>

          {/* Main Card */}
          <Card
            sx={{
              width: "100%",
              boxShadow: "0 16px 48px rgba(0, 0, 0, 0.4)",
              borderRadius: { xs: 3, sm: 5 },
              border: "1px solid rgba(255, 255, 255, 0.1)",
              backdropFilter: "blur(20px)",
              animation: "fadeInUp 0.6s ease-out 0.2s both",
              "@keyframes fadeInUp": {
                "0%": { opacity: 0, transform: "translateY(30px)" },
                "100%": { opacity: 1, transform: "translateY(0)" },
              },
            }}
          >
            <CardContent sx={{ p: { xs: 2, sm: 4 } }}>
              <Tabs
                value={tabValue}
                onChange={(_, v) => {
                  setTabValue(v);
                  setError("");
                }}
                variant="fullWidth"
                sx={{
                  mb: 2,
                  "& .MuiTab-root": {
                    fontWeight: 600,
                    fontSize: { xs: "0.875rem", sm: "1rem" },
                  },
                  "& .Mui-selected": {
                    color: theme.palette.primary.main,
                  },
                }}
              >
                <Tab icon={<LoginIcon />} iconPosition="start" label="Login" />
                <Tab
                  icon={<RegisterIcon />}
                  iconPosition="start"
                  label="Register"
                />
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
                    size={isMobile ? "small" : "medium"}
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
                    size={isMobile ? "small" : "medium"}
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size={isMobile ? "medium" : "large"}
                    disabled={loading}
                    sx={{
                      mt: 3,
                      mb: 2,
                      py: { xs: 1.5, sm: 2 },
                      fontSize: { xs: "0.875rem", sm: "1rem" },
                    }}
                  >
                    {loading ? "Logging in..." : "Login"}
                  </Button>
                  <Box sx={{ textAlign: "center" }}>
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
                    size={isMobile ? "small" : "medium"}
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
                    size={isMobile ? "small" : "medium"}
                  />

                  <Box sx={{ mt: 2 }}>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 1 }}
                    >
                      Phone Number (Required for WhatsApp) *
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item xs={4}>
                        <FormControl
                          fullWidth
                          size={isMobile ? "small" : "medium"}
                        >
                          <InputLabel>Code</InputLabel>
                          <Select
                            value={countryCode}
                            label="Code"
                            onChange={(e) => setCountryCode(e.target.value)}
                            disabled={loading}
                          >
                            {COUNTRY_CODES.map((country) => (
                              <MenuItem key={country.code} value={country.code}>
                                {country.code}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={8}>
                        <TextField
                          required
                          fullWidth
                          label="Phone Number"
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          disabled={loading}
                          autoComplete="tel"
                          placeholder="1234567"
                          size={isMobile ? "small" : "medium"}
                        />
                      </Grid>
                    </Grid>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ mt: 0.5, display: "block" }}
                    >
                      📱 You'll be able to chat with our AI assistant on
                      WhatsApp!
                    </Typography>
                  </Box>

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
                    size={isMobile ? "small" : "medium"}
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
                    error={
                      confirmPassword !== "" && password !== confirmPassword
                    }
                    helperText={
                      confirmPassword !== "" && password !== confirmPassword
                        ? "Passwords do not match"
                        : ""
                    }
                    size={isMobile ? "small" : "medium"}
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size={isMobile ? "medium" : "large"}
                    disabled={loading}
                    sx={{
                      mt: 3,
                      py: { xs: 1.5, sm: 2 },
                      fontSize: { xs: "0.875rem", sm: "1rem" },
                    }}
                  >
                    {loading ? "Creating Account..." : "Create Account"}
                  </Button>
                </form>
              </TabPanel>
            </CardContent>
          </Card>

          {/* Footer */}
          <Box
            sx={{
              mt: 4,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              animation: "fadeIn 1s ease-out 0.5s both",
            }}
          >
            <Typography
              variant="body2"
              sx={{
                color: "rgba(255, 255, 255, 0.7)",
                textAlign: "center",
                fontSize: { xs: "0.8125rem", sm: "0.875rem" },
              }}
            >
              © 2025 CareConnect. All rights reserved.
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: "rgba(255, 255, 255, 0.5)",
                textAlign: "center",
                fontSize: { xs: "0.75rem", sm: "0.8125rem" },
              }}
            >
              Powered by AI • Designed with Care
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
