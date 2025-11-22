/**
 * Voice state status display component
 */

import { Box, Typography, alpha } from '@mui/material';
import type { VoiceState } from './types';

interface VoiceStatusProps {
  voiceState: VoiceState;
  audioLevel: number;
  stateColor: string;
}

export default function VoiceStatus({
  voiceState,
  audioLevel,
  stateColor,
}: VoiceStatusProps) {
  const getStateText = () => {
    switch (voiceState) {
      case 'listening':
        return 'Listening... (speak naturally)';
      case 'processing':
        return 'Processing your request...';
      case 'speaking':
        return 'CareConnect is speaking...';
      default:
        return '☎️ Tap to start conversation';
    }
  };

  return (
    <Box
      sx={{
        textAlign: 'left',
      }}
    >
      <Typography
        variant="body1"
        sx={{
          color: stateColor,
          fontWeight: 600,
          fontSize: { xs: '0.875rem', sm: '1rem' },
          textShadow: `0 1px 3px ${alpha(stateColor, 0.2)}`,
        }}
      >
        {getStateText()}
      </Typography>
      {voiceState === 'listening' && (
        <Box
          sx={{
            display: 'flex',
            gap: 0.5,
            mt: 1,
          }}
        >
          {[...Array(5)].map((_, i) => (
            <Box
              key={i}
              sx={{
                width: 3,
                height: 16,
                bgcolor: stateColor,
                borderRadius: 1,
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
