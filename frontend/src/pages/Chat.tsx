import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
  IconButton,
  MenuItem,
  Paper,
  TextField,
  Typography,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { 
  Send as SendIcon, 
  SupportAgent as SupportAgentIcon,
  Phone as PhoneIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';
import type { ChatMessage, ToolResult } from '@/types/api';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [toolResults, setToolResults] = useState<ToolResult[]>([]);
  const [handoverDialogOpen, setHandoverDialogOpen] = useState(false);
  const [handoverSubject, setHandoverSubject] = useState('');
  const [handoverPhone, setHandoverPhone] = useState('');
  const [handoverPriority, setHandoverPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [handoverSuccess, setHandoverSuccess] = useState(false);
  const [confirmationCode, setConfirmationCode] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const chatMutation = useMutation({
    mutationFn: (messages: ChatMessage[]) => api.chat(messages, 1),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, data.message]);
      setToolResults(data.tool_results);
    },
  });

  const handoverMutation = useMutation({
    mutationFn: (data: { subject: string; phone: string | null; priority: string }) =>
      api.requestHandover(messages, data.subject, data.phone, data.priority),
    onSuccess: (data) => {
      setHandoverSuccess(true);
      setConfirmationCode(data.confirmation_code);
    },
  });

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    chatMutation.mutate([...messages, userMessage]);
  };

  const handleHandoverClick = () => {
    if (messages.length === 0) {
      alert('Please start a conversation first before requesting human assistance.');
      return;
    }
    setHandoverDialogOpen(true);
    setHandoverSuccess(false);
  };

  const handleHandoverSubmit = () => {
    if (!handoverSubject.trim()) {
      alert('Please provide a subject for your request.');
      return;
    }

    handoverMutation.mutate({
      subject: handoverSubject,
      phone: handoverPhone || null,
      priority: handoverPriority,
    });
  };

  const handleHandoverClose = () => {
    setHandoverDialogOpen(false);
    setHandoverSubject('');
    setHandoverPhone('');
    setHandoverPriority('medium');
    setHandoverSuccess(false);
    setConfirmationCode('');
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
            <Box sx={{ mt: 3 }}>
              <Button
                fullWidth
                variant="outlined"
                color="warning"
                startIcon={<SupportAgentIcon />}
                onClick={handleHandoverClick}
                disabled={messages.length === 0}
              >
                Talk to a Human
              </Button>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Request assistance from our care team
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Handover Dialog */}
      <Dialog open={handoverDialogOpen} onClose={handleHandoverClose} maxWidth="sm" fullWidth>
        {!handoverSuccess ? (
          <>
            <DialogTitle>Request Human Assistance</DialogTitle>
            <DialogContent>
              <DialogContentText>
                Our care team will review your conversation and contact you as soon as possible.
              </DialogContentText>
              <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
                <strong>For medical emergencies:</strong> Please call 911 immediately.
              </Alert>
              <TextField
                autoFocus
                margin="dense"
                label="Subject / Reason"
                type="text"
                fullWidth
                required
                value={handoverSubject}
                onChange={(e) => setHandoverSubject(e.target.value)}
                placeholder="e.g., Need help booking appointment, billing question"
                sx={{ mb: 2 }}
              />
              <TextField
                margin="dense"
                label="Phone Number (Optional)"
                type="tel"
                fullWidth
                value={handoverPhone}
                onChange={(e) => setHandoverPhone(e.target.value)}
                placeholder="+1-555-123-4567"
                InputProps={{
                  startAdornment: <PhoneIcon sx={{ mr: 1, color: 'action.active' }} />,
                }}
                sx={{ mb: 2 }}
              />
              <TextField
                select
                margin="dense"
                label="Priority"
                fullWidth
                value={handoverPriority}
                onChange={(e) => setHandoverPriority(e.target.value as any)}
              >
                <MenuItem value="low">Low - General inquiry</MenuItem>
                <MenuItem value="medium">Medium - Need assistance</MenuItem>
                <MenuItem value="high">High - Urgent matter</MenuItem>
                <MenuItem value="urgent">Urgent - Critical issue</MenuItem>
              </TextField>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleHandoverClose}>Cancel</Button>
              <Button
                onClick={handleHandoverSubmit}
                variant="contained"
                color="primary"
                disabled={handoverMutation.isPending || !handoverSubject.trim()}
              >
                {handoverMutation.isPending ? 'Submitting...' : 'Submit Request'}
              </Button>
            </DialogActions>
          </>
        ) : (
          <>
            <DialogTitle>Request Submitted</DialogTitle>
            <DialogContent>
              <Alert severity="success" sx={{ mb: 2 }}>
                Your request has been received!
              </Alert>
              <Typography variant="body1" gutterBottom>
                Thank you for reaching out. Our care team has been notified and will contact you within 24 hours.
              </Typography>
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Confirmation Code
                </Typography>
                <Typography variant="h6" color="primary">
                  {confirmationCode}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Please save this confirmation code for your records.
              </Typography>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleHandoverClose} variant="contained">
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Grid>
  );
}
