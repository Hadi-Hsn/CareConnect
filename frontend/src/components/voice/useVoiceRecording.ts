/**
 * Voice recording hook with Voice Activity Detection (VAD)
 * Uses hark for robust speech detection
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import hark from 'hark';
import type {
  VoiceRecordingOptions,
  VoiceRecordingState,
  VoiceRecordingControls,
  VADSettings,
} from './types';
import { DEFAULT_VAD_SETTINGS } from './types';

export function useVoiceRecording(
  options: VoiceRecordingOptions,
  vadSettings: VADSettings = DEFAULT_VAD_SETTINGS
): VoiceRecordingState & VoiceRecordingControls {
  const { autoMode, onTranscription, onSpeechToText, onStateChange } = options;

  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcription, setTranscription] = useState('');
  const [silenceProgress, setSilenceProgress] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const speechEventsRef = useRef<any>(null);
  const streamRef = useRef<MediaStream | null>(null);
  
  // Timing references
  const recordingStartTimeRef = useRef<number>(0);
  const lastSpeechTimeRef = useRef<number>(0);
  const silenceStartTimeRef = useRef<number | null>(null);
  const silenceTimerRef = useRef<number | null>(null);

  // Clean up resources
  const cleanup = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (silenceTimerRef.current) {
      clearInterval(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    if (speechEventsRef.current) {
      speechEventsRef.current.stop();
      speechEventsRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setSilenceProgress(0);
    silenceStartTimeRef.current = null;
  }, []);

  // Visualize audio levels
  const visualizeAudio = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

    const animate = () => {
      if (!isRecording || !analyserRef.current) {
        return;
      }

      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      const normalizedLevel = average / 255;

      setAudioLevel(normalizedLevel);

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();
  }, [isRecording]);

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      cleanup();

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100,
        },
      });

      streamRef.current = stream;

      // Setup audio context and analyzer for visualization
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext ||
          (window as any).webkitAudioContext)();
      }

      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      analyserRef.current.smoothingTimeConstant = vadSettings.smoothing;
      source.connect(analyserRef.current);

      // Setup hark for Voice Activity Detection
      if (autoMode) {
        const speechEvents = hark(stream, {
          threshold: -50,           // dB threshold for speech detection
          interval: 100,            // Check every 100ms
          play: false,
        });

        speechEvents.on('speaking', () => {
          const now = Date.now();
          lastSpeechTimeRef.current = now;
          
          // Reset silence detection
          if (silenceStartTimeRef.current) {
            silenceStartTimeRef.current = null;
            setSilenceProgress(0);
          }
        });

        speechEvents.on('stopped_speaking', () => {
          const now = Date.now();
          const recordingDuration = now - recordingStartTimeRef.current;

          // Only trigger silence detection if we've recorded enough
          if (recordingDuration >= vadSettings.minRecordingTime) {
            if (!silenceStartTimeRef.current) {
              silenceStartTimeRef.current = now;
              
              // Start silence progress timer
              if (silenceTimerRef.current) {
                clearInterval(silenceTimerRef.current);
              }
              
              silenceTimerRef.current = window.setInterval(() => {
                if (!silenceStartTimeRef.current) return;
                
                const elapsed = Date.now() - silenceStartTimeRef.current;
                const progress = Math.min((elapsed / vadSettings.silenceDuration) * 100, 100);
                setSilenceProgress(progress);

                if (elapsed >= vadSettings.silenceDuration) {
                  console.log('🔇 Silence detected - auto-stopping recording');
                  stopRecording();
                }
              }, 50);
            }
          }
        });

        speechEventsRef.current = speechEvents;
      }

      // Setup MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : 'audio/mp4';

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 128000,
      });

      audioChunksRef.current = [];
      recordingStartTimeRef.current = Date.now();
      lastSpeechTimeRef.current = Date.now();

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        cleanup();

        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorderRef.current?.mimeType || 'audio/webm',
        });

        // Only process if we have enough audio data (>100ms worth)
        if (audioBlob.size > 2000) {
          onStateChange('processing');

          try {
            const text = await onSpeechToText(audioBlob);
            if (text.trim()) {
              setTranscription(text);
              onTranscription(text);
            } else {
              onStateChange('idle');
            }
          } catch (error) {
            console.error('❌ Transcription error:', error);
            onStateChange('idle');
          }
        } else {
          console.log('⚠️ Audio too short, ignoring');
          onStateChange('idle');
        }
      };

      mediaRecorderRef.current.start(100); // Collect data every 100ms
      setIsRecording(true);
      onStateChange('listening');

      // Start visualization
      visualizeAudio();
    } catch (error) {
      console.error('❌ Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions.');
      cleanup();
    }
  }, [autoMode, onTranscription, onSpeechToText, onStateChange, vadSettings, cleanup, visualizeAudio]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    setAudioLevel(0);
  }, []);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      cleanup();
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [cleanup]);

  return {
    isRecording,
    audioLevel,
    transcription,
    silenceProgress,
    startRecording,
    stopRecording,
  };
}
