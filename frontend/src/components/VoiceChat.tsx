import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  useTheme,
  alpha,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  VolumeUp as VolumeUpIcon,
} from '@mui/icons-material';

interface VoiceChatProps {
  onTranscription: (text: string) => void;
  onSpeechToText: (audio: Blob) => Promise<string>;
  onTextToSpeech: (text: string) => Promise<Blob>;
  responseText?: string;
  isProcessing?: boolean;
}

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

export default function VoiceChat({
  onTranscription,
  onSpeechToText,
  onTextToSpeech,
  responseText,
  isProcessing = false,
}: VoiceChatProps) {
  const theme = useTheme();
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcription, setTranscription] = useState('');
  const [autoMode, setAutoMode] = useState(true); // Auto-detect when user stops speaking
  const [silenceTimer, setSilenceTimer] = useState<number | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastSpeechTimeRef = useRef<number>(Date.now());

  // VAD (Voice Activity Detection) thresholds
  const SILENCE_THRESHOLD = 0.02; // Audio level below this is considered silence
  const SILENCE_DURATION = 1500; // Stop recording after 1.5 seconds of silence
  const MIN_RECORDING_TIME = 1000; // Minimum recording time before checking for silence

  // Initialize audio context for visualizations
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
    };
  }, []);

  // Auto-play response when received
  useEffect(() => {
    if (responseText && voiceState === 'processing') {
      playResponse(responseText);
    }
  }, [responseText]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        } 
      });
      
      // Setup audio analyzer for visualization and VAD
      if (audioContextRef.current) {
        const source = audioContextRef.current.createMediaStreamSource(stream);
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        analyserRef.current.smoothingTimeConstant = 0.8;
        source.connect(analyserRef.current);
        visualizeAudio();
      }

      // Setup media recorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });
      audioChunksRef.current = [];
      lastSpeechTimeRef.current = Date.now();

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach((track) => track.stop());
        
        // Only process if we have enough audio data
        if (audioBlob.size > 1000) {
          setVoiceState('processing');
          
          try {
            const text = await onSpeechToText(audioBlob);
            if (text.trim()) {
              setTranscription(text);
              onTranscription(text);
            } else {
              setVoiceState('idle');
            }
          } catch (error) {
            console.error('Transcription error:', error);
            setVoiceState('idle');
          }
        } else {
          setVoiceState('idle');
        }
      };

      mediaRecorderRef.current.start(100); // Collect data every 100ms
      setVoiceState('listening');
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && voiceState === 'listening') {
      mediaRecorderRef.current.stop();
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
    }
  };

  const checkForSilence = (level: number) => {
    if (!autoMode || voiceState !== 'listening') return;

    const now = Date.now();
    const recordingDuration = now - lastSpeechTimeRef.current;

    // Don't check for silence in the first second of recording
    if (recordingDuration < MIN_RECORDING_TIME) return;

    if (level > SILENCE_THRESHOLD) {
      // User is speaking - reset silence timer
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
        silenceTimeoutRef.current = null;
      }
      setSilenceTimer(null);
    } else {
      // Silence detected - start or update timer
      if (!silenceTimeoutRef.current) {
        const startTime = Date.now();
        silenceTimeoutRef.current = setTimeout(() => {
          // User stopped speaking - auto-stop recording
          stopRecording();
        }, SILENCE_DURATION);

        // Update UI timer
        const updateTimer = () => {
          if (voiceState === 'listening') {
            const elapsed = Date.now() - startTime;
            setSilenceTimer(Math.min(elapsed, SILENCE_DURATION));
            if (elapsed < SILENCE_DURATION) {
              requestAnimationFrame(updateTimer);
            }
          }
        };
        updateTimer();
      }
    }
  };

  const visualizeAudio = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const animate = () => {
      if (voiceState !== 'listening') return;
      
      analyserRef.current?.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      const normalizedLevel = average / 255;
      
      setAudioLevel(normalizedLevel);
      
      // Check for silence in auto mode
      checkForSilence(normalizedLevel);
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    
    animate();
  };

  const playResponse = async (text: string) => {
    try {
      setVoiceState('speaking');
      const audioBlob = await onTextToSpeech(text);
      const audioUrl = URL.createObjectURL(audioBlob);
      
      audioRef.current = new Audio(audioUrl);
      audioRef.current.onended = () => {
        setVoiceState('idle');
        setTranscription('');
        URL.revokeObjectURL(audioUrl);
        
        // Auto-restart listening in auto mode
        if (autoMode) {
          setTimeout(() => {
            startRecording();
          }, 500);
        }
      };
      
      await audioRef.current.play();
    } catch (error) {
      console.error('Error playing audio:', error);
      setVoiceState('idle');
      
      // Auto-restart listening in auto mode
      if (autoMode) {
        setTimeout(() => {
          startRecording();
        }, 500);
      }
    }
  };

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setVoiceState('idle');
      setTranscription('');
    }
  };

  const getStateColor = () => {
    switch (voiceState) {
      case 'listening':
        return '#840132'; // Berytus Red
      case 'processing':
        return '#808080'; // Gray
      case 'speaking':
        return '#840132'; // Berytus Red
      default:
        return '#808080'; // Gray
    }
  };

  const getStateText = () => {
    switch (voiceState) {
      case 'listening':
        return autoMode ? 'Listening... (speak now)' : 'Recording...';
      case 'processing':
        return 'Processing your request...';
      case 'speaking':
        return 'CareConnect is speaking...';
      default:
        return autoMode ? 'Tap to start conversation' : 'Tap to speak';
    }
  };

  const handleMainButtonClick = () => {
    if (voiceState === 'idle') {
      startRecording();
    } else if (voiceState === 'listening') {
      stopRecording();
    } else if (voiceState === 'speaking') {
      stopSpeaking();
    }
  };

  const pulseScale = 1 + (audioLevel * 0.3);
  const glowIntensity = audioLevel * 20;
  const silenceProgress = silenceTimer ? (silenceTimer / SILENCE_DURATION) * 100 : 0;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        gap: { xs: 3, sm: 4 },
        padding: { xs: 2, sm: 4 },
      }}
    >
      {/* Auto mode toggle */}
      <FormControlLabel
        control={
          <Switch
            checked={autoMode}
            onChange={(e) => setAutoMode(e.target.checked)}
            disabled={voiceState !== 'idle'}
          />
        }
        label={
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Auto-detect when I stop speaking
          </Typography>
        }
      />

      {/* Main circular button */}
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Outer glow ring - animated during listening */}
        {voiceState === 'listening' && (
          <Box
            sx={{
              position: 'absolute',
              width: { xs: 200, sm: 280 },
              height: { xs: 200, sm: 280 },
              borderRadius: '50%',
              background: `radial-gradient(circle, ${alpha(getStateColor(), 0.4)} 0%, transparent 70%)`,
              filter: `blur(${glowIntensity}px)`,
              animation: 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 0.5 },
                '50%': { transform: 'scale(1.1)', opacity: 0.8 },
              },
            }}
          />
        )}

        {/* Silence detection progress ring */}
        {autoMode && voiceState === 'listening' && silenceProgress > 0 && (
          <Box
            sx={{
              position: 'absolute',
              width: { xs: 160, sm: 200 },
              height: { xs: 160, sm: 200 },
              borderRadius: '50%',
            }}
          >
            <svg
              width="100%"
              height="100%"
              viewBox="0 0 100 100"
              style={{ transform: 'rotate(-90deg)' }}
            >
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke={alpha(getStateColor(), 0.3)}
                strokeWidth="3"
              />
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke={getStateColor()}
                strokeWidth="3"
                strokeDasharray={`${2 * Math.PI * 45}`}
                strokeDashoffset={`${2 * Math.PI * 45 * (1 - silenceProgress / 100)}`}
                style={{ transition: 'stroke-dashoffset 0.1s linear' }}
              />
            </svg>
          </Box>
        )}

        {/* Animated rings during speaking */}
        {voiceState === 'speaking' && (
          <>
            {[0, 1, 2].map((i) => (
              <Box
                key={i}
                sx={{
                  position: 'absolute',
                  width: { xs: 120 + i * 30, sm: 180 + i * 40 },
                  height: { xs: 120 + i * 30, sm: 180 + i * 40 },
                  borderRadius: '50%',
                  border: `2px solid ${alpha(getStateColor(), 0.3)}`,
                  animation: `ripple 2s ease-out infinite ${i * 0.3}s`,
                  '@keyframes ripple': {
                    '0%': { transform: 'scale(0.8)', opacity: 1 },
                    '100%': { transform: 'scale(1.4)', opacity: 0 },
                  },
                }}
              />
            ))}
          </>
        )}

        {/* Main button */}
        <Paper
          elevation={8}
          sx={{
            width: { xs: 140, sm: 180 },
            height: { xs: 140, sm: 180 },
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `linear-gradient(135deg, ${getStateColor()} 0%, ${alpha(getStateColor(), 0.7)} 100%)`,
            cursor: voiceState !== 'processing' ? 'pointer' : 'default',
            transition: 'all 0.3s ease',
            transform: voiceState === 'listening' ? `scale(${pulseScale})` : 'scale(1)',
            boxShadow: `0 0 ${glowIntensity * 2}px ${alpha(getStateColor(), 0.5)}`,
            '&:hover': {
              transform: voiceState !== 'processing' ? 'scale(1.05)' : 'scale(1)',
            },
            '&:active': {
              transform: voiceState !== 'processing' ? 'scale(0.95)' : 'scale(1)',
            },
          }}
          onClick={handleMainButtonClick}
        >
          {voiceState === 'processing' || isProcessing ? (
            <CircularProgress size={60} sx={{ color: 'white' }} />
          ) : voiceState === 'listening' ? (
            <StopIcon sx={{ fontSize: { xs: 60, sm: 80 }, color: 'white' }} />
          ) : voiceState === 'speaking' ? (
            <VolumeUpIcon sx={{ fontSize: { xs: 60, sm: 80 }, color: 'white' }} />
          ) : (
            <MicIcon sx={{ fontSize: { xs: 60, sm: 80 }, color: 'white' }} />
          )}
        </Paper>

        {/* Microphone level indicator bars */}
        {voiceState === 'listening' && (
          <Box
            sx={{
              position: 'absolute',
              bottom: { xs: -50, sm: -60 },
              display: 'flex',
              gap: 1,
              alignItems: 'flex-end',
            }}
          >
            {[...Array(5)].map((_, i) => (
              <Box
                key={i}
                sx={{
                  width: { xs: 6, sm: 8 },
                  height: 4 + (audioLevel * 40) * (1 - Math.abs(i - 2) * 0.3),
                  backgroundColor: getStateColor(),
                  borderRadius: 1,
                  transition: 'height 0.1s ease',
                }}
              />
            ))}
          </Box>
        )}
      </Box>

      {/* Status text */}
      <Typography
        variant="h6"
        sx={{
          color: getStateColor(),
          fontWeight: 600,
          textAlign: 'center',
          fontSize: { xs: '1rem', sm: '1.25rem' },
        }}
      >
        {getStateText()}
      </Typography>

      {/* Transcription display */}
      {transcription && (
        <Paper
          elevation={2}
          sx={{
            padding: { xs: 2, sm: 3 },
            maxWidth: { xs: '100%', sm: 600 },
            width: '100%',
            borderRadius: 3,
            backgroundColor: alpha(theme.palette.background.paper, 0.9),
            borderLeft: '4px solid #840132',
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: theme.palette.text.secondary,
              textAlign: 'left',
              mb: 0.5,
              fontWeight: 600,
            }}
          >
            You said:
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: theme.palette.text.primary,
              textAlign: 'left',
              fontStyle: 'italic',
              fontSize: { xs: '0.875rem', sm: '1rem' },
            }}
          >
            "{transcription}"
          </Typography>
        </Paper>
      )}

      {/* Instructions */}
      {voiceState === 'idle' && (
        <Box sx={{ textAlign: 'center', maxWidth: { xs: 300, sm: 500 }, px: 2 }}>
          <Typography
            variant="body2"
            sx={{
              color: theme.palette.text.secondary,
              fontSize: { xs: '0.8rem', sm: '0.875rem' },
              mb: 2,
            }}
          >
            {autoMode 
              ? "Tap to start. Speak naturally and I'll respond when you pause. It's like a phone call!"
              : "Tap the microphone to start speaking. Tap the stop button when you're done."
            }
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: theme.palette.text.secondary,
              fontSize: { xs: '0.7rem', sm: '0.75rem' },
              display: 'block',
            }}
          >
            Try: "Book an appointment" • "Find a cardiologist" • "Lab test info"
          </Typography>
        </Box>
      )}
    </Box>
  );
}
