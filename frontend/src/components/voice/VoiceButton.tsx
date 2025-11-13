/**
 * Main voice interaction button component
 */

import { Paper, CircularProgress, alpha, Box } from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  VolumeUp as VolumeUpIcon,
} from '@mui/icons-material';
import type { VoiceState } from './types';

interface VoiceButtonProps {
  voiceState: VoiceState;
  audioLevel: number;
  stateColor: string;
  isProcessing: boolean;
  onClick: () => void;
}

export default function VoiceButton({
  voiceState,
  audioLevel,
  stateColor,
  isProcessing,
  onClick,
}: VoiceButtonProps) {
  const pulseScale = 1 + audioLevel * 0.3;
  const glowIntensity = audioLevel * 20;

  return (
    <>
      {/* Main button */}
      <Paper
        elevation={8}
        sx={{
          width: { xs: 160, sm: 200, md: 220 },
          height: { xs: 160, sm: 200, md: 220 },
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background:
            voiceState === 'idle'
              ? `linear-gradient(135deg, ${alpha(stateColor, 0.9)} 0%, ${alpha(stateColor, 0.7)} 100%)`
              : `linear-gradient(135deg, ${stateColor} 0%, ${alpha(stateColor, 0.8)} 100%)`,
          cursor: voiceState !== 'processing' ? 'pointer' : 'default',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          transform:
            voiceState === 'listening' ? `scale(${pulseScale})` : 'scale(1)',
          boxShadow:
            voiceState === 'idle'
              ? '0 8px 24px rgba(132, 1, 50, 0.3)'
              : `0 0 ${glowIntensity * 3}px ${alpha(stateColor, 0.6)}, 0 8px 32px ${alpha(stateColor, 0.4)}`,
          border: `3px solid ${alpha('#ffffff', 0.3)}`,
          position: 'relative',
          overflow: 'visible',
          '&:hover': {
            transform:
              voiceState !== 'processing' ? 'scale(1.08)' : 'scale(1)',
            boxShadow: `0 0 ${glowIntensity * 4}px ${alpha(stateColor, 0.7)}, 0 12px 40px ${alpha(stateColor, 0.5)}`,
          },
          '&:active': {
            transform:
              voiceState !== 'processing' ? 'scale(0.98)' : 'scale(1)',
          },
          '&::before':
            voiceState !== 'idle'
              ? {
                  content: '""',
                  position: 'absolute',
                  top: -10,
                  left: -10,
                  right: -10,
                  bottom: -10,
                  borderRadius: '50%',
                  background: `radial-gradient(circle, ${alpha(stateColor, 0.2)} 0%, transparent 70%)`,
                  animation: 'ripple 2s infinite ease-out',
                  '@keyframes ripple': {
                    '0%': { transform: 'scale(0.8)', opacity: 1 },
                    '100%': { transform: 'scale(1.3)', opacity: 0 },
                  },
                }
              : {},
        }}
        onClick={onClick}
      >
        {voiceState === 'processing' || isProcessing ? (
          <CircularProgress
            size={70}
            sx={{
              color: 'white',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              },
            }}
          />
        ) : voiceState === 'listening' ? (
          <StopIcon
            sx={{
              fontSize: { xs: 70, sm: 90, md: 100 },
              color: 'white',
              filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))',
            }}
          />
        ) : voiceState === 'speaking' ? (
          <VolumeUpIcon
            sx={{
              fontSize: { xs: 70, sm: 90, md: 100 },
              color: 'white',
              animation: 'bounce 0.6s infinite alternate',
              filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))',
              '@keyframes bounce': {
                '0%': { transform: 'scale(1)' },
                '100%': { transform: 'scale(1.1)' },
              },
            }}
          />
        ) : (
          <MicIcon
            sx={{
              fontSize: { xs: 70, sm: 90, md: 100 },
              color: 'white',
              filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))',
            }}
          />
        )}
      </Paper>

      {/* Microphone level indicator bars */}
      {voiceState === 'listening' && (
        <Box
          sx={{
            position: 'absolute',
            bottom: { xs: -50, sm: -60 },
            display: 'flex',
            gap: 1,
            alignItems: 'flex-end',
          }}
        >
          {[...Array(5)].map((_, i) => (
            <Box
              key={i}
              sx={{
                width: { xs: 6, sm: 8 },
                height: 4 + audioLevel * 40 * (1 - Math.abs(i - 2) * 0.3),
                backgroundColor: stateColor,
                borderRadius: 1,
                transition: 'height 0.1s ease',
              }}
            />
          ))}
        </Box>
      )}
    </>
  );
}
