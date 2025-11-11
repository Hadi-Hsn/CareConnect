import { createTheme } from '@mui/material/styles';

// AUB Theme Colors
const BERYTUS_RED = '#840132';
const BERYTUS_RED_LIGHT = '#a8013d';
const BERYTUS_RED_DARK = '#5e0124';
const AUB_GREEN = '#005A43';
const BLACK = '#000000';
const LIGHT_GRAY = '#808080';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: BERYTUS_RED,
      light: BERYTUS_RED_LIGHT,
      dark: BERYTUS_RED_DARK,
      contrastText: '#ffffff',
    },
    secondary: {
      main: AUB_GREEN,
      light: '#007a5e',
      dark: '#003d2e',
      contrastText: '#ffffff',
    },
    grey: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: LIGHT_GRAY,
      600: '#666666',
      700: '#4d4d4d',
      800: '#333333',
      900: '#1a1a1a',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    text: {
      primary: BLACK,
      secondary: LIGHT_GRAY,
    },
    error: {
      main: '#d32f2f',
      light: '#ef5350',
      dark: '#c62828',
    },
    warning: {
      main: '#ed6c02',
      light: '#ff9800',
      dark: '#e65100',
    },
    info: {
      main: '#0288d1',
      light: '#03a9f4',
      dark: '#01579b',
    },
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '3rem',
      fontWeight: 700,
      color: BLACK,
      letterSpacing: '-0.02em',
      '@media (max-width:600px)': {
        fontSize: '2rem',
      },
    },
    h2: {
      fontSize: '2.5rem',
      fontWeight: 700,
      color: BLACK,
      letterSpacing: '-0.01em',
      '@media (max-width:600px)': {
        fontSize: '1.75rem',
      },
    },
    h3: {
      fontSize: '2rem',
      fontWeight: 600,
      color: BLACK,
      '@media (max-width:600px)': {
        fontSize: '1.5rem',
      },
    },
    h4: {
      fontSize: '1.75rem',
      fontWeight: 600,
      color: BLACK,
      '@media (max-width:600px)': {
        fontSize: '1.25rem',
      },
    },
    h5: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: BLACK,
      '@media (max-width:600px)': {
        fontSize: '1.15rem',
      },
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 600,
      color: BLACK,
      '@media (max-width:600px)': {
        fontSize: '1rem',
      },
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.7,
      letterSpacing: '0.00938em',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
      letterSpacing: '0.01071em',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: '0.02em',
    },
    subtitle1: {
      fontSize: '1.125rem',
      fontWeight: 500,
      lineHeight: 1.75,
    },
    subtitle2: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.57,
    },
  },
  shape: {
    borderRadius: 16,
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(132, 1, 50, 0.05)',
    '0px 4px 8px rgba(132, 1, 50, 0.08)',
    '0px 6px 12px rgba(132, 1, 50, 0.1)',
    '0px 8px 16px rgba(132, 1, 50, 0.12)',
    '0px 10px 20px rgba(132, 1, 50, 0.14)',
    '0px 12px 24px rgba(132, 1, 50, 0.16)',
    '0px 14px 28px rgba(132, 1, 50, 0.18)',
    '0px 16px 32px rgba(132, 1, 50, 0.2)',
    '0px 18px 36px rgba(132, 1, 50, 0.22)',
    '0px 20px 40px rgba(132, 1, 50, 0.24)',
    '0px 22px 44px rgba(132, 1, 50, 0.26)',
    '0px 24px 48px rgba(132, 1, 50, 0.28)',
    '0px 26px 52px rgba(132, 1, 50, 0.3)',
    '0px 28px 56px rgba(132, 1, 50, 0.32)',
    '0px 30px 60px rgba(132, 1, 50, 0.34)',
    '0px 32px 64px rgba(132, 1, 50, 0.36)',
    '0px 34px 68px rgba(132, 1, 50, 0.38)',
    '0px 36px 72px rgba(132, 1, 50, 0.4)',
    '0px 38px 76px rgba(132, 1, 50, 0.42)',
    '0px 40px 80px rgba(132, 1, 50, 0.44)',
    '0px 42px 84px rgba(132, 1, 50, 0.46)',
    '0px 44px 88px rgba(132, 1, 50, 0.48)',
    '0px 46px 92px rgba(132, 1, 50, 0.5)',
    '0px 48px 96px rgba(132, 1, 50, 0.52)',
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          scrollbarColor: `${BERYTUS_RED} #f1f1f1`,
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#f1f1f1',
          },
          '&::-webkit-scrollbar-thumb': {
            background: BERYTUS_RED,
            borderRadius: '4px',
            '&:hover': {
              background: BERYTUS_RED_DARK,
            },
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 12,
          fontWeight: 600,
          fontSize: '0.9375rem',
          padding: '10px 24px',
          boxShadow: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 8px 16px rgba(132, 1, 50, 0.2)',
            transform: 'translateY(-2px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0 12px 24px rgba(132, 1, 50, 0.25)',
          },
        },
        containedPrimary: {
          background: `linear-gradient(135deg, ${BERYTUS_RED} 0%, ${BERYTUS_RED_DARK} 100%)`,
          '&:hover': {
            background: `linear-gradient(135deg, ${BERYTUS_RED_LIGHT} 0%, ${BERYTUS_RED} 100%)`,
          },
          '&:disabled': {
            background: 'rgba(0, 0, 0, 0.12)',
            color: 'rgba(0, 0, 0, 0.26)',
          },
        },
        containedSecondary: {
          background: `linear-gradient(135deg, ${AUB_GREEN} 0%, #003d2e 100%)`,
          '&:hover': {
            background: `linear-gradient(135deg, #007a5e 0%, ${AUB_GREEN} 100%)`,
          },
        },
        outlined: {
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
            backgroundColor: 'rgba(132, 1, 50, 0.04)',
          },
        },
        text: {
          '&:hover': {
            backgroundColor: 'rgba(132, 1, 50, 0.08)',
          },
        },
        sizeLarge: {
          padding: '12px 32px',
          fontSize: '1rem',
        },
        sizeSmall: {
          padding: '6px 16px',
          fontSize: '0.8125rem',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          border: '1px solid rgba(0, 0, 0, 0.06)',
          overflow: 'hidden',
          '&:hover': {
            boxShadow: '0 12px 32px rgba(132, 1, 50, 0.15)',
            transform: 'translateY(-4px)',
            borderColor: 'rgba(132, 1, 50, 0.2)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          backgroundImage: 'none',
        },
        elevation0: {
          boxShadow: 'none',
          border: '1px solid rgba(0, 0, 0, 0.08)',
        },
        elevation1: {
          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
        },
        elevation2: {
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
        },
        elevation3: {
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.1)',
        },
        elevation4: {
          boxShadow: '0 12px 32px rgba(0, 0, 0, 0.12)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            backgroundColor: '#fafbfc',
            transition: 'all 0.3s ease',
            '&:hover': {
              backgroundColor: '#ffffff',
              '& fieldset': {
                borderColor: BERYTUS_RED,
                borderWidth: '2px',
              },
            },
            '&.Mui-focused': {
              backgroundColor: '#ffffff',
              '& fieldset': {
                borderColor: BERYTUS_RED,
                borderWidth: '2px',
              },
            },
            '& fieldset': {
              borderColor: 'rgba(0, 0, 0, 0.12)',
              transition: 'all 0.3s ease',
            },
          },
          '& .MuiInputLabel-root': {
            fontWeight: 500,
            '&.Mui-focused': {
              color: BERYTUS_RED,
              fontWeight: 600,
            },
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: 'rgba(132, 1, 50, 0.08)',
            transform: 'scale(1.05)',
          },
          '&:active': {
            transform: 'scale(0.95)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          fontWeight: 500,
          fontSize: '0.8125rem',
          height: '28px',
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'scale(1.05)',
          },
        },
        colorPrimary: {
          backgroundColor: BERYTUS_RED,
          color: '#ffffff',
        },
        colorSecondary: {
          backgroundColor: AUB_GREEN,
          color: '#ffffff',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 16px rgba(132, 1, 50, 0.15)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRadius: 0,
          borderRight: '1px solid rgba(132, 1, 50, 0.08)',
          backgroundImage: 'linear-gradient(180deg, #ffffff 0%, #fafbfc 100%)',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          marginBottom: '4px',
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: 'rgba(132, 1, 50, 0.06)',
            transform: 'translateX(4px)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(132, 1, 50, 0.12)',
            borderLeft: `4px solid ${BERYTUS_RED}`,
            '&:hover': {
              backgroundColor: 'rgba(132, 1, 50, 0.16)',
            },
          },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          fontSize: '0.9375rem',
        },
        standardSuccess: {
          backgroundColor: 'rgba(46, 125, 50, 0.1)',
          color: '#1b5e20',
        },
        standardError: {
          backgroundColor: 'rgba(211, 47, 47, 0.1)',
          color: '#c62828',
        },
        standardWarning: {
          backgroundColor: 'rgba(237, 108, 2, 0.1)',
          color: '#e65100',
        },
        standardInfo: {
          backgroundColor: 'rgba(2, 136, 209, 0.1)',
          color: '#01579b',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 20,
          boxShadow: '0 24px 48px rgba(0, 0, 0, 0.2)',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: 'rgba(0, 0, 0, 0.08)',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          fontSize: '0.9375rem',
          minHeight: '48px',
          transition: 'all 0.2s ease',
          '&:hover': {
            color: BERYTUS_RED,
            opacity: 1,
          },
          '&.Mui-selected': {
            color: BERYTUS_RED,
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          height: '3px',
          borderRadius: '3px 3px 0 0',
          backgroundColor: BERYTUS_RED,
        },
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },
});
