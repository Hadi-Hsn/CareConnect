# Voice Chat Components

This directory contains modular voice chat components with improved Voice Activity Detection (VAD) using the `hark` library for a smooth, phone-call-like experience.

## 📁 Structure

```
voice/
├── types.ts                    # Shared TypeScript types and interfaces
├── useVoiceRecording.ts        # Hook for audio recording with VAD
├── useAudioPlayback.ts         # Hook for TTS audio playback
├── AudioVisualizer.tsx         # Visual feedback component
├── VoiceButton.tsx             # Main interaction button
├── VoiceControls.tsx           # Mode toggle and controls
├── VoiceStatus.tsx             # Status text display
├── TranscriptionDisplay.tsx    # Transcription result display
└── VoiceInstructions.tsx       # Instructions and examples
```

## 🎤 Key Features

### Voice Activity Detection (VAD)
- Uses `hark` library for robust speech detection
- Auto-detects when user stops speaking
- Configurable thresholds and timing
- Visual progress indicator for silence detection

### Phone Call Mode
- Seamless conversation flow
- Auto-restart after responses
- Natural pause detection
- Real-time audio level visualization

## 🔧 Configuration

VAD settings can be configured via `DEFAULT_VAD_SETTINGS` in `types.ts`:

```typescript
{
  silenceThreshold: 0.01,     // Lower = more sensitive
  silenceDuration: 1500,      // ms of silence before stopping
  minRecordingTime: 500,      // Min recording before checking silence
  smoothing: 0.85             // Audio analysis smoothing (0-1)
}
```

## 🎯 Usage

The main `VoiceChat` component automatically composes all sub-components:

```tsx
<VoiceChat
  onTranscription={(text) => console.log(text)}
  onSpeechToText={async (audio) => await sttService(audio)}
  onTextToSpeech={async (text) => await ttsService(text)}
  responseText={aiResponse}
  isProcessing={loading}
/>
```

## 🔌 Dependencies

- `hark`: Voice activity detection
- `@mui/material`: UI components
- `@mui/icons-material`: Icons

## 🛠️ Development

All components are fully typed with TypeScript and follow React best practices:
- Custom hooks for logic separation
- Memoization where appropriate
- Proper cleanup of resources
- Accessibility considerations
