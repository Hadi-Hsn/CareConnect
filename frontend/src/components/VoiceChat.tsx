import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  useTheme,
  alpha,
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
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);

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
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Setup audio analyzer for visualization
      if (audioContextRef.current) {
        const source = audioContextRef.current.createMediaStreamSource(stream);
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        source.connect(analyserRef.current);
        visualizeAudio();
      }

      // Setup media recorder
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach((track) => track.stop());
        
        setVoiceState('processing');
        
        try {
          const text = await onSpeechToText(audioBlob);
          setTranscription(text);
          onTranscription(text);
        } catch (error) {
          console.error('Transcription error:', error);
          setVoiceState('idle');
        }
      };

      mediaRecorderRef.current.start();
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
    }
  };

  const visualizeAudio = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const animate = () => {
      if (voiceState !== 'listening') return;
      
      analyserRef.current?.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setAudioLevel(average / 255);
      
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
      };
      
      await audioRef.current.play();
    } catch (error) {
      console.error('Error playing audio:', error);
      setVoiceState('idle');
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
        return '#808080'; // Light Gray
      case 'speaking':
        return '#840132'; // Berytus Red
      default:
        return '#808080'; // Light Gray
    }
  };

  const getStateText = () => {
    switch (voiceState) {
      case 'listening':
        return 'Listening...';
      case 'processing':
        return 'Processing...';
      case 'speaking':
        return 'Speaking...';
      default:
        return 'Tap to speak';
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
            variant="body1"
            sx={{
              color: theme.palette.text.primary,
              textAlign: 'center',
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
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            textAlign: 'center',
            maxWidth: { xs: 300, sm: 400 },
            fontSize: { xs: '0.8rem', sm: '0.875rem' },
            px: 2,
          }}
        >
          Tap the microphone to start speaking. The AI will listen, transcribe your message, and
          respond with voice.
        </Typography>
      )}
    </Box>
  );
}
