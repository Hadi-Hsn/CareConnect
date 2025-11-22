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
      }}
    >
      <FormControlLabel
        control={
          <Switch
            checked={autoMode}
            onChange={(e) => onAutoModeChange(e.target.checked)}
            disabled={voiceState !== 'idle'}
            size="small"
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
              fontSize: { xs: '0.8125rem', sm: '0.875rem' },
            }}
          >
            ☎️ Phone call mode
          </Typography>
        }
      />
    </Box>
  );
}
