/**
 * Voice chat controls and mode toggle
 */

import { Box, Typography, Switch, FormControlLabel } from '@mui/material';
import type { VoiceState } from './types';

interface VoiceControlsProps {
  autoMode: boolean;
  onAutoModeChange: (enabled: boolean) => void;
  voiceState: VoiceState;
}

export default function VoiceControls({
  autoMode,
  onAutoModeChange,
  voiceState,
}: VoiceControlsProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        p: { xs: 1.5, sm: 2 },
        borderRadius: 4,
        bgcolor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
        border: '1px solid rgba(132, 1, 50, 0.1)',
      }}
    >
      <FormControlLabel
        control={
          <Switch
            checked={autoMode}
            onChange={(e) => onAutoModeChange(e.target.checked)}
            disabled={voiceState !== 'idle'}
            sx={{
              '& .MuiSwitch-switchBase.Mui-checked': {
                color: '#840132',
                '&:hover': {
                  backgroundColor: 'rgba(132, 1, 50, 0.08)',
                },
              },
              '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                backgroundColor: '#840132',
              },
            }}
          />
        }
        label={
          <Typography
            variant="body2"
            sx={{
              color: 'text.primary',
              fontWeight: 500,
              fontSize: { xs: '0.875rem', sm: '0.9375rem' },
            }}
          >
            🎯 Phone call mode (auto-detect silence)
          </Typography>
        }
      />
    </Box>
  );
}
