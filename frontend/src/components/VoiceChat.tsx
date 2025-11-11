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
  const silenceTimeoutRef = useRef<number | null>(null);
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
        gap: { xs: 3, sm: 4, md: 5 },
        padding: { xs: 2, sm: 4, md: 6 },
        position: 'relative',
        background: 'radial-gradient(circle at center, rgba(132, 1, 50, 0.03) 0%, transparent 70%)',
      }}
    >
      {/* Auto mode toggle with enhanced styling */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          p: { xs: 1.5, sm: 2 },
          borderRadius: 4,
          bgcolor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
          border: '1px solid rgba(132, 1, 50, 0.1)',
        }}
      >
        <FormControlLabel
          control={
            <Switch
              checked={autoMode}
              onChange={(e) => setAutoMode(e.target.checked)}
              disabled={voiceState !== 'idle'}
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
                color: theme.palette.text.primary,
                fontWeight: 500,
                fontSize: { xs: '0.875rem', sm: '0.9375rem' },
              }}
            >
              Auto-detect when I stop speaking
            </Typography>
          }
        />
      </Box>

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
          <>
            <Box
              sx={{
                position: 'absolute',
                width: { xs: 220, sm: 300, md: 320 },
                height: { xs: 220, sm: 300, md: 320 },
                borderRadius: '50%',
                background: `radial-gradient(circle, ${alpha(getStateColor(), 0.5)} 0%, transparent 70%)`,
                filter: `blur(${glowIntensity}px)`,
                animation: 'pulse 2s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%, 100%': { transform: 'scale(1)', opacity: 0.5 },
                  '50%': { transform: 'scale(1.15)', opacity: 0.8 },
                },
              }}
            />
            <Box
              sx={{
                position: 'absolute',
                width: { xs: 200, sm: 260, md: 280 },
                height: { xs: 200, sm: 260, md: 280 },
                borderRadius: '50%',
                border: `2px solid ${alpha(getStateColor(), 0.3)}`,
                animation: 'rotate 10s linear infinite',
                '@keyframes rotate': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
              }}
            >
              <Box
                sx={{
                  position: 'absolute',
                  top: '10%',
                  left: '50%',
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: getStateColor(),
                  transform: 'translateX(-50%)',
                  boxShadow: `0 0 20px ${alpha(getStateColor(), 0.6)}`,
                }}
              />
            </Box>
          </>
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
            width: { xs: 160, sm: 200, md: 220 },
            height: { xs: 160, sm: 200, md: 220 },
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: voiceState === 'idle' 
              ? `linear-gradient(135deg, ${alpha(getStateColor(), 0.9)} 0%, ${alpha(getStateColor(), 0.7)} 100%)`
              : `linear-gradient(135deg, ${getStateColor()} 0%, ${alpha(getStateColor(), 0.8)} 100%)`,
            cursor: voiceState !== 'processing' ? 'pointer' : 'default',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: voiceState === 'listening' ? `scale(${pulseScale})` : 'scale(1)',
            boxShadow: voiceState === 'idle'
              ? '0 8px 24px rgba(132, 1, 50, 0.3)'
              : `0 0 ${glowIntensity * 3}px ${alpha(getStateColor(), 0.6)}, 0 8px 32px ${alpha(getStateColor(), 0.4)}`,
            border: `3px solid ${alpha('#ffffff', 0.3)}`,
            position: 'relative',
            overflow: 'visible',
            '&:hover': {
              transform: voiceState !== 'processing' ? 'scale(1.08)' : 'scale(1)',
              boxShadow: `0 0 ${glowIntensity * 4}px ${alpha(getStateColor(), 0.7)}, 0 12px 40px ${alpha(getStateColor(), 0.5)}`,
            },
            '&:active': {
              transform: voiceState !== 'processing' ? 'scale(0.98)' : 'scale(1)',
            },
            '&::before': voiceState !== 'idle' ? {
              content: '""',
              position: 'absolute',
              top: -10,
              left: -10,
              right: -10,
              bottom: -10,
              borderRadius: '50%',
              background: `radial-gradient(circle, ${alpha(getStateColor(), 0.2)} 0%, transparent 70%)`,
              animation: 'ripple 2s infinite ease-out',
              '@keyframes ripple': {
                '0%': { transform: 'scale(0.8)', opacity: 1 },
                '100%': { transform: 'scale(1.3)', opacity: 0 },
              },
            } : {},
          }}
          onClick={handleMainButtonClick}
        >
          {voiceState === 'processing' || isProcessing ? (
            <CircularProgress 
              size={70} 
              sx={{ 
                color: 'white',
                '& .MuiCircularProgress-circle': {
                  strokeLinecap: 'round',
                },
              }} 
            />
          ) : voiceState === 'listening' ? (
            <StopIcon 
              sx={{ 
                fontSize: { xs: 70, sm: 90, md: 100 }, 
                color: 'white',
                filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))',
              }} 
            />
          ) : voiceState === 'speaking' ? (
            <VolumeUpIcon 
              sx={{ 
                fontSize: { xs: 70, sm: 90, md: 100 }, 
                color: 'white',
                animation: 'bounce 0.6s infinite alternate',
                filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))',
                '@keyframes bounce': {
                  '0%': { transform: 'scale(1)' },
                  '100%': { transform: 'scale(1.1)' },
                },
              }} 
            />
          ) : (
            <MicIcon 
              sx={{ 
                fontSize: { xs: 70, sm: 90, md: 100 }, 
                color: 'white',
                filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))',
              }} 
            />
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
      <Box
        sx={{
          textAlign: 'center',
          px: 2,
        }}
      >
        <Typography
          variant="h5"
          sx={{
            color: getStateColor(),
            fontWeight: 700,
            textAlign: 'center',
            fontSize: { xs: '1.25rem', sm: '1.5rem', md: '1.75rem' },
            mb: 1,
            textShadow: `0 2px 8px ${alpha(getStateColor(), 0.3)}`,
            letterSpacing: '0.5px',
          }}
        >
          {getStateText()}
        </Typography>
        {voiceState === 'listening' && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              gap: 0.5,
              mt: 2,
            }}
          >
            {[...Array(5)].map((_, i) => (
              <Box
                key={i}
                sx={{
                  width: { xs: 4, sm: 5 },
                  height: { xs: 20, sm: 24 },
                  bgcolor: getStateColor(),
                  borderRadius: 2,
                  animation: `wave 1s ease-in-out infinite ${i * 0.1}s`,
                  opacity: 0.7 + (audioLevel * 0.3),
                  '@keyframes wave': {
                    '0%, 100%': { transform: 'scaleY(0.5)' },
                    '50%': { transform: 'scaleY(1.2)' },
                  },
                }}
              />
            ))}
          </Box>
        )}
      </Box>

      {/* Transcription display */}
      {transcription && (
        <Paper
          elevation={3}
          sx={{
            padding: { xs: 2.5, sm: 3.5 },
            maxWidth: { xs: '100%', sm: 600, md: 700 },
            width: '100%',
            borderRadius: 4,
            backgroundColor: alpha(theme.palette.background.paper, 0.95),
            backdropFilter: 'blur(10px)',
            borderLeft: '5px solid #840132',
            boxShadow: '0 8px 24px rgba(132, 1, 50, 0.15)',
            animation: 'slideIn 0.3s ease-out',
            '@keyframes slideIn': {
              '0%': { opacity: 0, transform: 'translateY(20px)' },
              '100%': { opacity: 1, transform: 'translateY(0)' },
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <MicIcon sx={{ color: '#840132', mr: 1, fontSize: '1.25rem' }} />
            <Typography
              variant="subtitle2"
              sx={{
                color: theme.palette.text.secondary,
                fontWeight: 700,
                letterSpacing: '0.5px',
                textTransform: 'uppercase',
                fontSize: '0.75rem',
              }}
            >
              You said:
            </Typography>
          </Box>
          <Typography
            variant="body1"
            sx={{
              color: theme.palette.text.primary,
              textAlign: 'left',
              fontStyle: 'italic',
              fontSize: { xs: '0.9375rem', sm: '1.0625rem' },
              lineHeight: 1.7,
              pl: 2,
              borderLeft: '2px solid rgba(132, 1, 50, 0.2)',
            }}
          >
            "{transcription}"
          </Typography>
        </Paper>
      )}

      {/* Instructions */}
      {voiceState === 'idle' && (
        <Box
          sx={{
            textAlign: 'center',
            maxWidth: { xs: 340, sm: 500, md: 600 },
            px: { xs: 2, sm: 3 },
          }}
        >
          <Typography
            variant="body1"
            sx={{
              color: theme.palette.text.secondary,
              fontSize: { xs: '0.9375rem', sm: '1rem' },
              mb: 3,
              lineHeight: 1.7,
              fontWeight: 500,
            }}
          >
            {autoMode 
              ? "🎤 Tap to start. Speak naturally and I'll respond when you pause. It's like a phone call!"
              : "🎤 Tap the microphone to start speaking. Tap the stop button when you're done."
            }
          </Typography>
          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 1.5,
              justifyContent: 'center',
              mb: 2,
            }}
          >
            {[
              { icon: '📅', text: 'Book an appointment' },
              { icon: '👨‍⚕️', text: 'Find a cardiologist' },
              { icon: '🧪', text: 'Lab test info' },
            ].map((item, idx) => (
              <Box
                key={idx}
                sx={{
                  px: 2,
                  py: 1.5,
                  borderRadius: 3,
                  bgcolor: 'rgba(132, 1, 50, 0.05)',
                  border: '1px solid rgba(132, 1, 50, 0.1)',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'rgba(132, 1, 50, 0.1)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(132, 1, 50, 0.15)',
                  },
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: theme.palette.text.primary,
                    fontSize: { xs: '0.8125rem', sm: '0.875rem' },
                    fontWeight: 500,
                  }}
                >
                  {item.icon} {item.text}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
}
