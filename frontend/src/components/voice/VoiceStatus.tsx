/**
 * Voice state status display component
 */

import { Box, Typography, alpha } from '@mui/material';
import type { VoiceState } from './types';

interface VoiceStatusProps {
  voiceState: VoiceState;
  audioLevel: number;
  stateColor: string;
  autoMode: boolean;
}

export default function VoiceStatus({
  voiceState,
  audioLevel,
  stateColor,
  autoMode,
}: VoiceStatusProps) {
  const getStateText = () => {
    switch (voiceState) {
      case 'listening':
        return autoMode ? 'Listening... (speak naturally)' : 'Recording...';
      case 'processing':
        return 'Processing your request...';
      case 'speaking':
        return 'CareConnect is speaking...';
      default:
        return autoMode
          ? '☎️ Tap to start phone call mode'
          : 'Tap to speak';
    }
  };

  return (
    <Box
      sx={{
        textAlign: 'center',
        px: 2,
      }}
    >
      <Typography
        variant="h5"
        sx={{
          color: stateColor,
          fontWeight: 700,
          textAlign: 'center',
          fontSize: { xs: '1.25rem', sm: '1.5rem', md: '1.75rem' },
          mb: 1,
          textShadow: `0 2px 8px ${alpha(stateColor, 0.3)}`,
          letterSpacing: '0.5px',
        }}
      >
        {getStateText()}
      </Typography>
      {voiceState === 'listening' && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            gap: 0.5,
            mt: 2,
          }}
        >
          {[...Array(5)].map((_, i) => (
            <Box
              key={i}
              sx={{
                width: { xs: 4, sm: 5 },
                height: { xs: 20, sm: 24 },
                bgcolor: stateColor,
                borderRadius: 2,
                animation: `wave 1s ease-in-out infinite ${i * 0.1}s`,
                opacity: 0.7 + audioLevel * 0.3,
                '@keyframes wave': {
                  '0%, 100%': { transform: 'scaleY(0.5)' },
                  '50%': { transform: 'scaleY(1.2)' },
                },
              }}
            />
          ))}
        </Box>
      )}
    </Box>
  );
}
