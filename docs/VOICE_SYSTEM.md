# Voice Interaction System

## Overview

CareConnect now supports **voice-based interactions** similar to ChatGPT's voice mode, allowing patients to speak naturally with the AI assistant. The system provides a seamless conversational experience using OpenAI's Whisper (speech-to-text) and TTS (text-to-speech) technologies.

## Features

### Patient Experience

1. **Voice Mode Toggle**
   - Switch between text chat and voice mode with a single click
   - Circular microphone button with visual feedback
   - Real-time audio level visualization

2. **Speaking to the AI**
   - Tap the microphone to start recording
   - See live audio waveform while speaking
   - Tap again to stop and send your message
   - Automatic transcription using OpenAI Whisper

3. **Listening to Responses**
   - AI responses are automatically converted to speech
   - Visual indication when AI is speaking
   - Animated pulsing effects during playback
   - Can interrupt or stop playback at any time

4. **Visual Feedback States**
   - **Idle** (Gray): Tap to speak
   - **Listening** (Red): Recording your voice with waveform animation
   - **Processing** (Orange): Transcribing and generating response
   - **Speaking** (Blue): Playing AI response with ripple effects

### Call Center-Like Experience

The voice interface is designed to mimic professional call center interactions:

- Natural conversation flow
- Clear visual indicators of system state
- Professional voice options (alloy, echo, fable, onyx, nova, shimmer)
- Seamless handover to human agents when needed
- Persistent conversation history

## Architecture

### Backend Components

#### 1. Voice Service (`app/services/voice_service.py`)

Core service handling OpenAI API integration:

```python
class VoiceService:
    async def text_to_speech(text: str, voice: str | None = None) -> bytes:
        """Convert text to speech using OpenAI TTS"""
        
    async def speech_to_text(audio_file: BinaryIO, filename: str, language: str) -> str:
        """Convert speech to text using OpenAI Whisper"""
```

**Key Features:**
- Async/await for non-blocking operations
- Configurable voice selection
- MP3 audio format output
- Support for multiple audio input formats (WebM, MP3, WAV, etc.)
- Automatic language detection

#### 2. Voice API Endpoints (`app/api/v1/voice.py`)

Two main endpoints:

##### POST `/api/v1/voice/text-to-speech`
Convert text to speech audio.

**Request:**
```json
{
  "text": "Hello, how can I help you today?",
  "voice": "alloy"  // Optional: alloy, echo, fable, onyx, nova, shimmer
}
```

**Response:**
- Audio stream in MP3 format
- Headers: `Content-Type: audio/mpeg`

**Authentication:** Required (Bearer token)

##### POST `/api/v1/voice/speech-to-text`
Convert audio to text.

**Request:**
- Form data with audio file (multipart/form-data)
- `audio`: Audio file (WebM, MP3, WAV, etc.)
- `language`: Language code (default: 'en')

**Response:**
```json
{
  "text": "I would like to book an appointment with Dr. Smith"
}
```

**Authentication:** Required (Bearer token)
**Max File Size:** 25MB

### Frontend Components

#### 1. VoiceChat Component (`src/components/VoiceChat.tsx`)

Beautiful, interactive voice UI with:

**Visual Elements:**
- Large circular button (180px) with gradient background
- Pulsing glow effect during listening
- Ripple animations during speaking
- Real-time audio level bars (5 bars)
- Transcription display box

**State Management:**
```typescript
type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';
```

**Props:**
```typescript
interface VoiceChatProps {
  onTranscription: (text: string) => void;      // Called when speech is transcribed
  onSpeechToText: (audio: Blob) => Promise<string>;  // STT API call
  onTextToSpeech: (text: string) => Promise<Blob>;   // TTS API call
  responseText?: string;                         // AI response to speak
  isProcessing?: boolean;                        // Show loading state
}
```

**Key Features:**
- Web Audio API for real-time visualization
- MediaRecorder API for audio capture
- Audio context for waveform analysis
- Automatic audio playback management
- Responsive design with Material-UI

#### 2. Chat Page Integration (`src/pages/Chat.tsx`)

Voice mode toggle in the chat interface:

**UI Changes:**
- Two toggle buttons (Chat icon / Mic icon)
- Conditional rendering: text chat or voice UI
- Seamless state synchronization
- Persistent message history across modes

**Integration Flow:**
```typescript
// Voice handlers
handleVoiceTranscription(text) -> Add to messages -> Send to chat API
chatMutation.onSuccess(response) -> Set lastResponseText -> Auto-play TTS
```

### Configuration (`app/core/config.py`)

```python
# OpenAI Voice Settings
openai_tts_model: str = "tts-1"      # or "tts-1-hd" for higher quality
openai_tts_voice: str = "alloy"      # Default voice
openai_stt_model: str = "whisper-1"  # Speech-to-text model
```

**Available Voices:**
- `alloy`: Neutral, balanced voice
- `echo`: Warm, friendly voice
- `fable`: Expressive, storytelling voice
- `onyx`: Deep, authoritative voice
- `nova`: Young, energetic voice
- `shimmer`: Soft, gentle voice

## User Workflow

### Complete Voice Interaction Flow

```
1. User opens Chat page
   ↓
2. Clicks microphone icon to enable voice mode
   ↓
3. Taps circular microphone button
   ↓
4. Browser requests microphone permission
   ↓
5. User speaks: "I need to book an appointment"
   ↓
6. Audio waveform visualizes in real-time
   ↓
7. User taps stop button
   ↓
8. Recording sent to /api/v1/voice/speech-to-text
   ↓
9. Whisper transcribes audio
   ↓
10. Transcription displayed and sent to chat API
    ↓
11. AI generates response text
    ↓
12. Response sent to /api/v1/voice/text-to-speech
    ↓
13. TTS generates audio
    ↓
14. Audio automatically plays with visual feedback
    ↓
15. User can tap to interrupt or let it finish
    ↓
16. Loop continues for natural conversation
```

## API Integration

### Frontend API Client (`src/lib/api.ts`)

```typescript
class ApiClient {
  async textToSpeech(text: string, voice?: string): Promise<Blob> {
    const { data } = await this.client.post(
      '/voice/text-to-speech',
      { text, voice },
      { responseType: 'blob' }
    );
    return data;
  }

  async speechToText(audioBlob: Blob, language: string = 'en'): Promise<string> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.webm');
    formData.append('language', language);
    
    const { data } = await this.client.post('/voice/speech-to-text', formData);
    return data.text;
  }
}
```

## Browser Compatibility

### Required Browser Features
- **MediaRecorder API**: For audio recording (Chrome 49+, Firefox 25+, Safari 14.1+)
- **Web Audio API**: For waveform visualization (All modern browsers)
- **MediaDevices.getUserMedia**: For microphone access (All modern browsers)
- **Audio element**: For playback (Universal support)

### Browser Permissions
The application requires:
1. **Microphone access**: User must grant permission on first use
2. **Autoplay audio**: Most browsers allow audio in response to user interaction

### Tested Browsers
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ⚠️ Mobile browsers may have autoplay restrictions

## Security & Privacy

### Authentication
- All voice endpoints require JWT authentication
- User identity tracked for audit logging

### Data Handling
- Audio recordings are **not stored** on the server
- Transcriptions pass through OpenAI API (follow OpenAI's data policy)
- TTS audio generated on-demand, not cached
- Conversation history stored in database per existing policy

### Rate Limiting
- Standard API rate limits apply (60 requests/minute)
- Large audio files (>25MB) rejected
- Consider implementing per-user voice quotas

### HTTPS Requirement
- Voice features require HTTPS in production
- Microphone access blocked on insecure origins (except localhost)

## Performance Optimization

### Audio Compression
- Frontend records in WebM format (efficient compression)
- Backend returns MP3 (broad compatibility, small size)
- Typical sizes:
  - 10 seconds of speech: ~50KB (WebM) / ~80KB (MP3)
  - 30 seconds of speech: ~150KB (WebM) / ~240KB (MP3)

### Latency Optimization
- OpenAI Whisper: ~1-3 seconds for transcription
- OpenAI TTS: ~1-2 seconds for audio generation
- Total round-trip: 3-7 seconds (acceptable for conversational UX)

### Caching Strategy
Consider implementing:
- Response text caching for common queries
- Audio caching for frequently used phrases
- Client-side audio buffer for instant playback

## Testing Checklist

### Backend Tests
- [ ] TTS with default voice
- [ ] TTS with custom voice (all 6 voices)
- [ ] TTS with long text (>1000 characters)
- [ ] STT with WebM audio
- [ ] STT with MP3 audio
- [ ] STT with different languages (en, es, fr)
- [ ] Authentication required for both endpoints
- [ ] File size limit enforcement (>25MB rejected)
- [ ] Error handling for OpenAI API failures

### Frontend Tests
- [ ] Voice mode toggle works
- [ ] Microphone permission request appears
- [ ] Recording starts on tap
- [ ] Waveform visualizes audio levels
- [ ] Recording stops on second tap
- [ ] Transcription displays correctly
- [ ] Audio plays automatically after response
- [ ] Can interrupt audio playback
- [ ] Visual states change correctly (idle → listening → processing → speaking)
- [ ] Error handling for no microphone access
- [ ] Switching between text/voice modes preserves conversation

### Integration Tests
- [ ] Complete voice conversation (3+ turns)
- [ ] Voice to handover transition
- [ ] Voice mode on mobile devices
- [ ] Voice mode with slow network (3G simulation)
- [ ] Multiple concurrent users

## Deployment Considerations

### Environment Variables
Ensure `.env` includes:
```bash
OPENAI_API_KEY=sk-...
OPENAI_TTS_MODEL=tts-1          # or tts-1-hd
OPENAI_TTS_VOICE=alloy
OPENAI_STT_MODEL=whisper-1
```

### Docker Setup
Voice features work out-of-the-box with existing Docker configuration. No additional setup needed.

### Cost Estimation
OpenAI Pricing (as of 2024):
- **Whisper (STT)**: $0.006 per minute of audio
- **TTS Standard (tts-1)**: $0.015 per 1K characters
- **TTS HD (tts-1-hd)**: $0.030 per 1K characters

Example cost for 100 conversations (avg 5 minutes each, 500 words response):
- STT: 500 minutes × $0.006 = $3.00
- TTS (standard): 50K characters × $0.015 / 1000 = $0.75
- **Total: ~$3.75 for 100 voice conversations**

### Scaling Considerations
- Voice API calls are CPU-light (offloaded to OpenAI)
- Network bandwidth is the main concern
- Consider CDN for static audio assets
- Monitor OpenAI API quotas and rate limits

## Monitoring & Analytics

### Metrics to Track
- Voice mode activation rate
- Average conversation length (voice vs text)
- STT accuracy (based on user corrections)
- TTS playback completion rate
- Voice-to-handover conversion rate
- API latency percentiles (p50, p95, p99)

### Logging
```python
logger.info("text_to_speech", text_length=len(text), voice=voice)
logger.info("speech_to_text", audio_size=len(contents), language=language)
```

## Future Enhancements

### Short-term (Next Sprint)
1. **Voice selection UI**: Let users choose their preferred AI voice
2. **Speed control**: 0.5x to 2x playback speed
3. **Transcription editing**: Allow users to correct STT mistakes
4. **Audio trimming**: Remove silence from recordings
5. **Keyboard shortcuts**: Space to record, Esc to cancel

### Medium-term (Next Month)
6. **Conversation memory**: "Remember what we discussed last time"
7. **Background noise suppression**: Filter out ambient noise
8. **Voice activity detection**: Auto-start recording on speech
9. **Sentiment analysis**: Detect frustration and offer human handover
10. **Multi-language support**: Automatic language detection

### Long-term (Future Roadmap)
11. **Voice biometrics**: Patient identification via voice
12. **Real-time streaming**: Stream TTS audio as it generates
13. **Offline mode**: Local STT/TTS for privacy-conscious users
14. **Voice commands**: "Book appointment", "Find doctor", etc.
15. **Accessibility features**: Adjustable volume, captions

## Troubleshooting

### Common Issues

**Problem:** Microphone permission denied
- **Solution:** User must manually enable in browser settings
- Chrome: Site Settings → Permissions → Microphone
- Firefox: Page Info → Permissions → Use the Microphone

**Problem:** No audio playback
- **Solution:** Check browser autoplay policy
- Ensure user has interacted with page before playback
- Test with volume up and not muted

**Problem:** Poor transcription accuracy
- **Solution:** 
  - Speak clearly and slowly
  - Reduce background noise
  - Use higher quality microphone
  - Check audio levels (not too quiet/loud)

**Problem:** High latency (>10 seconds)
- **Solution:**
  - Check network speed
  - Verify OpenAI API status
  - Monitor backend logs for timeouts
  - Consider upgrading to tts-1-hd for better quality

**Problem:** Audio cuts off mid-sentence
- **Solution:**
  - Increase max audio length
  - Check MediaRecorder settings
  - Verify file size under 25MB limit

## Support & Contact

For voice feature issues:
1. Check browser console for JavaScript errors
2. Verify microphone permissions granted
3. Test with `/api/v1/health` endpoint
4. Review backend logs for OpenAI API errors
5. Contact development team with:
   - Browser type and version
   - Audio file format
   - Error messages
   - Network conditions

---

**Last Updated:** October 31, 2025
**Version:** 1.0.0
**Author:** CareConnect Development Team
