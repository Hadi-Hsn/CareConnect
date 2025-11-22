/**
 * Audio playback hook for text-to-speech responses
 */

import { useState, useRef, useCallback } from 'react';
import type {
  AudioPlaybackOptions,
  AudioPlaybackState,
  AudioPlaybackControls,
} from './types';

export function useAudioPlayback(
  options: AudioPlaybackOptions
): AudioPlaybackState & AudioPlaybackControls {
  const { onTextToSpeech, onStateChange, autoRestartRecording, autoMode, onResponseComplete } = options;

  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);

  // Clean up audio resources
  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
    setIsPlaying(false);
  }, []);

  // Play TTS response
  const playResponse = useCallback(
    async (text: string) => {
      try {
        cleanup();
        onStateChange('speaking');

        const audioBlob = await onTextToSpeech(text);
        const audioUrl = URL.createObjectURL(audioBlob);
        audioUrlRef.current = audioUrl;

        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        setIsPlaying(true);

        audio.onended = () => {
          cleanup();
          onStateChange('idle');

          // Notify parent that response is complete
          if (onResponseComplete) {
            onResponseComplete();
          }

          // Auto-restart listening in auto mode after a brief pause
          if (autoMode && autoRestartRecording) {
            setTimeout(() => {
              autoRestartRecording();
            }, 500);
          }
        };

        audio.onerror = (error) => {
          console.error('❌ Audio playback error:', error);
          cleanup();
          onStateChange('idle');

          // Auto-restart listening even on error
          if (autoMode && autoRestartRecording) {
            setTimeout(() => {
              autoRestartRecording();
            }, 500);
          }
        };

        await audio.play();
      } catch (error) {
        console.error('❌ Error playing audio:', error);
        cleanup();
        onStateChange('idle');

        // Auto-restart listening on error
        if (autoMode && autoRestartRecording) {
          setTimeout(() => {
            autoRestartRecording();
          }, 500);
        }
      }
    },
    [onTextToSpeech, onStateChange, autoMode, autoRestartRecording, cleanup]
  );

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    cleanup();
    onStateChange('idle');
  }, [cleanup, onStateChange]);

  return {
    isPlaying,
    playResponse,
    stopSpeaking,
  };
}
