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
      elevation={1}
      sx={{
        padding: { xs: 1, sm: 1.5 },
        borderRadius: 2,
        backgroundColor: alpha(theme.palette.background.paper, 0.8),
        borderLeft: '3px solid #840132',
        boxShadow: '0 2px 8px rgba(132, 1, 50, 0.1)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
        <MicIcon sx={{ color: '#840132', fontSize: '1rem', mt: 0.25 }} />
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.primary,
            fontStyle: 'italic',
            fontSize: { xs: '0.8125rem', sm: '0.875rem' },
            lineHeight: 1.4,
          }}
        >
          "{transcription}"
        </Typography>
      </Box>
    </Paper>
  );
}
