import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  IconButton,
  Paper,
  TextField,
  Typography,
  Chip,
  CircularProgress,
} from '@mui/material';
import { Send as SendIcon, ThumbUp, ThumbDown } from '@mui/icons-material';
import { api } from '@/lib/api';
import type { ChatMessage, ToolResult } from '@/types/api';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [toolResults, setToolResults] = useState<ToolResult[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const chatMutation = useMutation({
    mutationFn: (messages: ChatMessage[]) => api.chat(messages, 1),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, data.message]);
      setToolResults(data.tool_results);
    },
  });

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    chatMutation.mutate([...messages, userMessage]);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Grid container spacing={3} sx={{ height: 'calc(100vh - 100px)' }}>
      <Grid item xs={12} md={8}>
        <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h5">Chat with CareConnect</Typography>
            <Typography variant="body2" color="text.secondary">
              I can help you book appointments, find providers, and answer facility questions
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
            {messages.map((msg, idx) => (
              <Box
                key={idx}
                sx={{
                  mb: 2,
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: msg.role === 'user' ? 'primary.main' : 'background.paper',
                    color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  }}
                >
                  <Typography variant="body1">{msg.content}</Typography>
                </Paper>
              </Box>
            ))}
            {chatMutation.isPending && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              disabled={chatMutation.isPending}
            />
            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={chatMutation.isPending || !input.trim()}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Context
            </Typography>
            {toolResults.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Recent Actions
                </Typography>
                {toolResults.map((result, idx) => (
                  <Chip
                    key={idx}
                    label={result.name}
                    size="small"
                    color={result.success ? 'success' : 'error'}
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            )}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Quick Actions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Book an appointment
                <br />
                • Find a provider
                <br />
                • Check lab requirements
                <br />
                • Get directions
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
