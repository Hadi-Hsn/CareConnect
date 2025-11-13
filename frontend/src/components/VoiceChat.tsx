/**
 * VoiceChat - Main voice interaction component
 * Refactored into smaller, manageable components with improved VAD using hark
 */

import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import type { VoiceChatProps, VoiceState } from './voice/types';
import { useVoiceRecording } from './voice/useVoiceRecording';
import { useAudioPlayback } from './voice/useAudioPlayback';
import VoiceControls from './voice/VoiceControls';
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
}: VoiceChatProps) {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [autoMode, setAutoMode] = useState(true);

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
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        gap: { xs: 3, sm: 4, md: 5 },
        padding: { xs: 2, sm: 4, md: 6 },
        position: 'relative',
        background:
          'radial-gradient(circle at center, rgba(132, 1, 50, 0.03) 0%, transparent 70%)',
      }}
    >
      {/* Auto mode toggle */}
      <VoiceControls
        autoMode={autoMode}
        onAutoModeChange={setAutoMode}
        voiceState={voiceState}
      />

      {/* Main voice interaction area */}
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
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

      {/* Status text */}
      <VoiceStatus
        voiceState={voiceState}
        audioLevel={recording.audioLevel}
        stateColor={stateColor}
        autoMode={autoMode}
      />

      {/* Transcription display */}
      <TranscriptionDisplay transcription={recording.transcription} />

      {/* Instructions */}
      <VoiceInstructions voiceState={voiceState} autoMode={autoMode} />
    </Box>
  );
}
