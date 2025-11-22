/**
 * Voice chat instructions and examples
 */

import { Box, Typography, useTheme } from '@mui/material';
import type { VoiceState } from './types';

interface VoiceInstructionsProps {
  voiceState: VoiceState;
}

const exampleQueries = [
  { icon: '📅', text: 'Book an appointment' },
  { icon: '👨‍⚕️', text: 'Find a cardiologist' },
  { icon: '🧪', text: 'Lab test info' },
];

export default function VoiceInstructions({
  voiceState,
}: VoiceInstructionsProps) {
  const theme = useTheme();

  if (voiceState !== 'idle') return null;

  return (
    <Box
      sx={{
        textAlign: 'left',
      }}
    >
      <Typography
        variant="body2"
        sx={{
          color: theme.palette.text.secondary,
          fontSize: { xs: '0.8125rem', sm: '0.875rem' },
          mb: 1.5,
          lineHeight: 1.5,
        }}
      >
        ☎️ Just like a phone call! Speak naturally and I'll respond when you pause.
      </Typography>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 0.75,
        }}
      >
        <Typography
          variant="caption"
          sx={{
            color: theme.palette.text.secondary,
            fontSize: '0.75rem',
            fontWeight: 500,
          }}
        >
          Try asking:
        </Typography>
        {exampleQueries.map((item, idx) => (
          <Typography
            key={idx}
            variant="caption"
            sx={{
              color: theme.palette.text.primary,
              fontSize: '0.75rem',
              pl: 1,
            }}
          >
            {item.icon} {item.text}
          </Typography>
        ))}
      </Box>
    </Box>
  );
}
