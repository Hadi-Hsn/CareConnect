/**
 * VoiceChat - Professional voice interaction component
 * Clean, minimal interface with conversation display and stop controls
 */

import { useState, useEffect } from 'react';
import { Box, IconButton, Typography, alpha, LinearProgress, Button } from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  VolumeUp as SpeakingIcon,
  HourglassEmpty as ProcessingIcon,
} from '@mui/icons-material';
import type { VoiceChatProps, VoiceState } from './voice/types';
import { useVoiceRecording } from './voice/useVoiceRecording';
import { useAudioPlayback } from './voice/useAudioPlayback';

export default function VoiceChat({
  onTranscription,
  onSpeechToText,
  onTextToSpeech,
  responseText,
  onResponseComplete,
}: VoiceChatProps) {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const autoMode = true;

  // Voice recording hook
  const recording = useVoiceRecording({
    autoMode,
    onTranscription,
    onSpeechToText,
    onStateChange: setVoiceState,
  });

  // Audio playback hook
  const playback = useAudioPlayback({
    onTextToSpeech,
    onStateChange: setVoiceState,
    autoRestartRecording: recording.startRecording,
    autoMode,
    onResponseComplete,
  });

  // Auto-play response when received
  useEffect(() => {
    if (responseText && voiceState === 'processing') {
      playback.playResponse(responseText);
    }
  }, [responseText, voiceState, playback]);

  // Handle main action
  const handleAction = () => {
    if (voiceState === 'idle') {
      recording.startRecording();
    } else if (voiceState === 'listening') {
      recording.stopRecording();
    } else if (voiceState === 'speaking') {
      playback.stopSpeaking();
    }
  };

  // Get status info
  const getStatusInfo = () => {
    switch (voiceState) {
      case 'listening':
        return { text: 'Listening...', color: '#840132', icon: <MicIcon /> };
      case 'processing':
        return { text: 'Processing...', color: '#666', icon: <ProcessingIcon /> };
      case 'speaking':
        return { text: 'Speaking...', color: '#2e7d32', icon: <SpeakingIcon /> };
      default:
        return { text: 'Click to speak', color: '#666', icon: <MicIcon /> };
    }
  };

  const status = getStatusInfo();
  const isActive = voiceState !== 'idle';
  const canStop = voiceState === 'listening' || voiceState === 'speaking';

  return (
    <Box sx={{ p: 3 }}>
      {/* Main Control Area */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 3,
        }}
      >
        {/* Main Button */}
        <Box sx={{ position: 'relative' }}>
          <IconButton
            onClick={handleAction}
            disabled={voiceState === 'processing'}
            sx={{
              width: 72,
              height: 72,
              bgcolor: isActive ? status.color : '#f5f5f5',
              color: isActive ? '#fff' : '#666',
              transition: 'all 0.2s ease',
              '&:hover': {
                bgcolor: isActive ? status.color : '#e0e0e0',
                transform: 'scale(1.05)',
              },
              '&.Mui-disabled': {
                bgcolor: '#e0e0e0',
                color: '#999',
              },
            }}
          >
            {canStop ? <StopIcon sx={{ fontSize: 32 }} /> : status.icon}
          </IconButton>
          
          {/* Listening indicator ring */}
          {voiceState === 'listening' && (
            <Box
              sx={{
                position: 'absolute',
                inset: -8,
                borderRadius: '50%',
                border: '3px solid',
                borderColor: alpha('#840132', 0.3),
                animation: 'pulse 1.5s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%, 100%': { transform: 'scale(1)', opacity: 1 },
                  '50%': { transform: 'scale(1.1)', opacity: 0.5 },
                },
              }}
            />
          )}
        </Box>

        {/* Status Text */}
        <Box sx={{ minWidth: 150 }}>
          <Typography
            variant="body1"
            sx={{
              fontWeight: 600,
              color: status.color,
            }}
          >
            {status.text}
          </Typography>
          
          {/* Audio level indicator */}
          {voiceState === 'listening' && (
            <LinearProgress
              variant="determinate"
              value={Math.min(recording.audioLevel * 100, 100)}
              sx={{
                mt: 1,
                height: 4,
                borderRadius: 2,
                bgcolor: alpha('#840132', 0.1),
                '& .MuiLinearProgress-bar': {
                  bgcolor: '#840132',
                  borderRadius: 2,
                },
              }}
            />
          )}
          
          {/* Silence countdown */}
          {voiceState === 'listening' && recording.silenceProgress > 0 && (
            <Typography variant="caption" sx={{ color: 'text.secondary', mt: 0.5, display: 'block' }}>
              Sending in {Math.ceil((1 - recording.silenceProgress) * 2)}s...
            </Typography>
          )}
        </Box>

        {/* Stop Button (visible when active) */}
        {canStop && (
          <Button
            variant="outlined"
            size="small"
            onClick={handleAction}
            startIcon={<StopIcon />}
            sx={{
              borderColor: 'divider',
              color: 'text.secondary',
              textTransform: 'none',
              '&:hover': {
                borderColor: '#d32f2f',
                color: '#d32f2f',
              },
            }}
          >
            Stop
          </Button>
        )}
      </Box>

      {/* Transcription Display */}
      {recording.transcription && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            bgcolor: '#fff',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 500 }}>
            You said:
          </Typography>
          <Typography variant="body2" sx={{ mt: 0.5, color: 'text.primary' }}>
            "{recording.transcription}"
          </Typography>
        </Box>
      )}

      {/* Instructions */}
      <Typography
        variant="caption"
        sx={{
          display: 'block',
          textAlign: 'center',
          mt: 2,
          color: 'text.disabled',
        }}
      >
        {voiceState === 'idle' && 'Click the microphone to start, pause to auto-send'}
        {voiceState === 'listening' && 'Speak clearly, pause when done'}
        {voiceState === 'speaking' && 'Click Stop to interrupt'}
      </Typography>
    </Box>
  );
}
