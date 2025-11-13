/**
 * Voice chat instructions and examples
 */

import { Box, Typography, useTheme } from '@mui/material';
import type { VoiceState } from './types';

interface VoiceInstructionsProps {
  voiceState: VoiceState;
  autoMode: boolean;
}

const exampleQueries = [
  { icon: '📅', text: 'Book an appointment' },
  { icon: '👨‍⚕️', text: 'Find a cardiologist' },
  { icon: '🧪', text: 'Lab test info' },
];

export default function VoiceInstructions({
  voiceState,
  autoMode,
}: VoiceInstructionsProps) {
  const theme = useTheme();

  if (voiceState !== 'idle') return null;

  return (
    <Box
      sx={{
        textAlign: 'center',
        maxWidth: { xs: 340, sm: 500, md: 600 },
        px: { xs: 2, sm: 3 },
      }}
    >
      <Typography
        variant="body1"
        sx={{
          color: theme.palette.text.secondary,
          fontSize: { xs: '0.9375rem', sm: '1rem' },
          mb: 3,
          lineHeight: 1.7,
          fontWeight: 500,
        }}
      >
        {autoMode
          ? "☎️ Just like a phone call! Tap to start, speak naturally, and I'll respond when you pause. Hands-free and effortless."
          : "🎤 Tap the microphone to start speaking. Tap the stop button when you're done."}
      </Typography>
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 1.5,
          justifyContent: 'center',
          mb: 2,
        }}
      >
        {exampleQueries.map((item, idx) => (
          <Box
            key={idx}
            sx={{
              px: 2,
              py: 1.5,
              borderRadius: 3,
              bgcolor: 'rgba(132, 1, 50, 0.05)',
              border: '1px solid rgba(132, 1, 50, 0.1)',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'rgba(132, 1, 50, 0.1)',
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 12px rgba(132, 1, 50, 0.15)',
              },
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: theme.palette.text.primary,
                fontSize: { xs: '0.8125rem', sm: '0.875rem' },
                fontWeight: 500,
              }}
            >
              {item.icon} {item.text}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
}
