/**
 * Voice chat types and interfaces
 */

export type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

export interface VoiceChatProps {
  onTranscription: (text: string) => void;
  onSpeechToText: (audio: Blob) => Promise<string>;
  onTextToSpeech: (text: string) => Promise<Blob>;
  responseText?: string;
  isProcessing?: boolean;
  onResponseComplete?: () => void;
}

export interface VoiceRecordingOptions {
  autoMode: boolean;
  onTranscription: (text: string) => void;
  onSpeechToText: (audio: Blob) => Promise<string>;
  onStateChange: (state: VoiceState) => void;
}

export interface VoiceRecordingState {
  isRecording: boolean;
  audioLevel: number;
  transcription: string;
  silenceProgress: number;
}

export interface VoiceRecordingControls {
  startRecording: () => Promise<void>;
  stopRecording: () => void;
}

export interface AudioPlaybackOptions {
  onTextToSpeech: (text: string) => Promise<Blob>;
  onStateChange: (state: VoiceState) => void;
  autoRestartRecording?: () => void;
  autoMode: boolean;
  onResponseComplete?: () => void;
}

export interface AudioPlaybackState {
  isPlaying: boolean;
}

export interface AudioPlaybackControls {
  playResponse: (text: string) => Promise<void>;
  stopSpeaking: () => void;
}

// Voice Activity Detection settings
export interface VADSettings {
  silenceThreshold: number;
  silenceDuration: number;
  minRecordingTime: number;
  smoothing: number;
}

export const DEFAULT_VAD_SETTINGS: VADSettings = {
  silenceThreshold: 0.01,    // More sensitive - detects quieter speech
  silenceDuration: 1500,     // 1.5 seconds of silence before stopping
  minRecordingTime: 500,     // Minimum 0.5 seconds before checking for silence
  smoothing: 0.85,           // Higher smoothing for more stable detection
};
