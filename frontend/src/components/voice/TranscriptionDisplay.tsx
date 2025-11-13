/**
 * Transcription display component
 */

import { Paper, Typography, Box, alpha, useTheme } from '@mui/material';
import { Mic as MicIcon } from '@mui/icons-material';

interface TranscriptionDisplayProps {
  transcription: string;
}

export default function TranscriptionDisplay({
  transcription,
}: TranscriptionDisplayProps) {
  const theme = useTheme();

  if (!transcription) return null;

  return (
    <Paper
      elevation={3}
      sx={{
        padding: { xs: 2.5, sm: 3.5 },
        maxWidth: { xs: '100%', sm: 600, md: 700 },
        width: '100%',
        borderRadius: 4,
        backgroundColor: alpha(theme.palette.background.paper, 0.95),
        backdropFilter: 'blur(10px)',
        borderLeft: '5px solid #840132',
        boxShadow: '0 8px 24px rgba(132, 1, 50, 0.15)',
        animation: 'slideIn 0.3s ease-out',
        '@keyframes slideIn': {
          '0%': { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <MicIcon sx={{ color: '#840132', mr: 1, fontSize: '1.25rem' }} />
        <Typography
          variant="subtitle2"
          sx={{
            color: theme.palette.text.secondary,
            fontWeight: 700,
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
            fontSize: '0.75rem',
          }}
        >
          You said:
        </Typography>
      </Box>
      <Typography
        variant="body1"
        sx={{
          color: theme.palette.text.primary,
          textAlign: 'left',
          fontStyle: 'italic',
          fontSize: { xs: '0.9375rem', sm: '1.0625rem' },
          lineHeight: 1.7,
          pl: 2,
          borderLeft: '2px solid rgba(132, 1, 50, 0.2)',
        }}
      >
        "{transcription}"
      </Typography>
    </Paper>
  );
}
