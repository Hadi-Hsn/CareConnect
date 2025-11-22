/**
 * VoiceChat - Main voice interaction component
 * Refactored into smaller, manageable components with improved VAD using hark
 */

import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import type { VoiceChatProps, VoiceState } from './voice/types';
import { useVoiceRecording } from './voice/useVoiceRecording';
import { useAudioPlayback } from './voice/useAudioPlayback';
import AudioVisualizer from './voice/AudioVisualizer';
import VoiceButton from './voice/VoiceButton';
import VoiceStatus from './voice/VoiceStatus';
import TranscriptionDisplay from './voice/TranscriptionDisplay';
import VoiceInstructions from './voice/VoiceInstructions';

export default function VoiceChat({
  onTranscription,
  onSpeechToText,
  onTextToSpeech,
  responseText,
  isProcessing = false,
  onResponseComplete,
}: VoiceChatProps) {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const autoMode = true; // Always use phone call mode

  // Voice recording hook with improved VAD
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

  // Main button click handler
  const handleMainButtonClick = () => {
    if (voiceState === 'idle') {
      recording.startRecording();
    } else if (voiceState === 'listening') {
      recording.stopRecording();
    } else if (voiceState === 'speaking') {
      playback.stopSpeaking();
    }
  };

  // Get state color
  const getStateColor = () => {
    switch (voiceState) {
      case 'listening':
      case 'speaking':
        return '#840132'; // Berytus Red
      case 'processing':
        return '#808080'; // Gray
      default:
        return '#808080'; // Gray
    }
  };

  const stateColor = getStateColor();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: { xs: 2, sm: 3 },
        padding: { xs: 2, sm: 2.5 },
        background: 'linear-gradient(135deg, rgba(132, 1, 50, 0.04) 0%, rgba(132, 1, 50, 0.01) 100%)',
        borderRadius: 0,
        minHeight: { xs: '120px', sm: '140px' },
      }}
    >
      {/* Left Section: Status and Instructions */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 1.5,
          flex: 1,
          minWidth: 0, // Allow text to truncate
        }}
      >
        {/* Status text */}
        <VoiceStatus
          voiceState={voiceState}
          audioLevel={recording.audioLevel}
          stateColor={stateColor}
        />

        {/* Transcription display - compact */}
        {recording.transcription && (
          <TranscriptionDisplay transcription={recording.transcription} />
        )}
      </Box>

      {/* Center Section: Main Voice Button with Visualizer */}
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        {/* Audio visualizations */}
        <AudioVisualizer
          voiceState={voiceState}
          audioLevel={recording.audioLevel}
          silenceProgress={recording.silenceProgress}
          stateColor={stateColor}
        />

        {/* Main button */}
        <VoiceButton
          voiceState={voiceState}
          audioLevel={recording.audioLevel}
          stateColor={stateColor}
          isProcessing={isProcessing}
          onClick={handleMainButtonClick}
        />
      </Box>

      {/* Right Section: Instructions */}
      <Box
        sx={{
          display: { xs: 'none', md: 'flex' },
          flexDirection: 'column',
          gap: 1,
          flex: 1,
          minWidth: 0,
        }}
      >
        <VoiceInstructions voiceState={voiceState} />
      </Box>
    </Box>
  );
}
