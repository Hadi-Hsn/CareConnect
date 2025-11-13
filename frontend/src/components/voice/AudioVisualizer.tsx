/**
 * Audio visualization component
 * Displays visual feedback for audio levels and voice state
 */

import { Box, alpha } from '@mui/material';
import type { VoiceState } from './types';

interface AudioVisualizerProps {
  voiceState: VoiceState;
  audioLevel: number;
  silenceProgress: number;
  stateColor: string;
}

export default function AudioVisualizer({
  voiceState,
  audioLevel,
  silenceProgress,
  stateColor,
}: AudioVisualizerProps) {
  const glowIntensity = audioLevel * 20;

  return (
    <Box
      sx={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Outer glow ring - animated during listening */}
      {voiceState === 'listening' && (
        <>
          <Box
            sx={{
              position: 'absolute',
              width: { xs: 220, sm: 300, md: 320 },
              height: { xs: 220, sm: 300, md: 320 },
              borderRadius: '50%',
              background: `radial-gradient(circle, ${alpha(stateColor, 0.5)} 0%, transparent 70%)`,
              filter: `blur(${glowIntensity}px)`,
              animation: 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 0.5 },
                '50%': { transform: 'scale(1.15)', opacity: 0.8 },
              },
            }}
          />
          <Box
            sx={{
              position: 'absolute',
              width: { xs: 200, sm: 260, md: 280 },
              height: { xs: 200, sm: 260, md: 280 },
              borderRadius: '50%',
              border: `2px solid ${alpha(stateColor, 0.3)}`,
              animation: 'rotate 10s linear infinite',
              '@keyframes rotate': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' },
              },
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: '10%',
                left: '50%',
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: stateColor,
                transform: 'translateX(-50%)',
                boxShadow: `0 0 20px ${alpha(stateColor, 0.6)}`,
              }}
            />
          </Box>
        </>
      )}

      {/* Silence detection progress ring */}
      {voiceState === 'listening' && silenceProgress > 0 && (
        <Box
          sx={{
            position: 'absolute',
            width: { xs: 160, sm: 200 },
            height: { xs: 160, sm: 200 },
            borderRadius: '50%',
          }}
        >
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 100 100"
            style={{ transform: 'rotate(-90deg)' }}
          >
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={alpha(stateColor, 0.3)}
              strokeWidth="3"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={stateColor}
              strokeWidth="3"
              strokeDasharray={`${2 * Math.PI * 45}`}
              strokeDashoffset={`${2 * Math.PI * 45 * (1 - silenceProgress / 100)}`}
              style={{ transition: 'stroke-dashoffset 0.1s linear' }}
            />
          </svg>
        </Box>
      )}

      {/* Animated rings during speaking */}
      {voiceState === 'speaking' && (
        <>
          {[0, 1, 2].map((i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                width: { xs: 120 + i * 30, sm: 180 + i * 40 },
                height: { xs: 120 + i * 30, sm: 180 + i * 40 },
                borderRadius: '50%',
                border: `2px solid ${alpha(stateColor, 0.3)}`,
                animation: `ripple 2s ease-out infinite ${i * 0.3}s`,
                '@keyframes ripple': {
                  '0%': { transform: 'scale(0.8)', opacity: 1 },
                  '100%': { transform: 'scale(1.4)', opacity: 0 },
                },
              }}
            />
          ))}
        </>
      )}
    </Box>
  );
}
