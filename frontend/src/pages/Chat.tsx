import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  MenuItem,
  Paper,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  alpha,
  InputAdornment,
  Tabs,
  Tab,
} from "@mui/material";
import {
  Send as SendIcon,
  Phone as PhoneIcon,
  Mic as MicIcon,
  Keyboard as KeyboardIcon,
  Refresh as RefreshIcon,
  SupportAgent as SupportAgentIcon,
} from "@mui/icons-material";
import { api } from "@/lib/api";
import type { ChatMessage, ToolResult } from "@/types/api";
import VoiceChat from "@/components/VoiceChat";

// Storage helpers
const STORAGE_PREFIX = "careconnect_chat";

const getSessionKey = (userId?: number) =>
  `${STORAGE_PREFIX}_session_${userId ?? "anonymous"}`;

const getMessagesKey = (userId?: number) =>
  `${STORAGE_PREFIX}_messages_${userId ?? "anonymous"}`;

const getDraftKey = (userId?: number) =>
  `${STORAGE_PREFIX}_draft_${userId ?? "anonymous"}`;

interface ChatSession {
  id: string;
  startedAt: string;
  lastActivity: string;
}

function getCurrentSession(sessionKey: string): ChatSession {
  const stored = localStorage.getItem(sessionKey);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      // Invalid session, create new one
    }
  }
  return createNewSession(sessionKey);
}

function createNewSession(sessionKey: string): ChatSession {
  const session: ChatSession = {
    id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    startedAt: new Date().toISOString(),
    lastActivity: new Date().toISOString(),
  };
  localStorage.setItem(sessionKey, JSON.stringify(session));
  return session;
}

function updateSessionActivity(sessionKey: string, session: ChatSession): void {
  session.lastActivity = new Date().toISOString();
  localStorage.setItem(sessionKey, JSON.stringify(session));
}

function loadMessagesFromStorage(messagesKey: string): ChatMessage[] {
  const stored = localStorage.getItem(messagesKey);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return [];
    }
  }
  return [];
}

function saveMessagesToStorage(
  messagesKey: string,
  messages: ChatMessage[],
): void {
  localStorage.setItem(messagesKey, JSON.stringify(messages));
}

function getStoredUserId(): number | undefined {
  const userStr = localStorage.getItem("user");
  if (!userStr) return undefined;
  try {
    const user = JSON.parse(userStr);
    return user.id;
  } catch {
    return undefined;
  }
}

export default function ChatPage() {
  const currentUserId = getStoredUserId();
  const sessionKey = getSessionKey(currentUserId);
  const messagesKey = getMessagesKey(currentUserId);
  const draftKey = getDraftKey(currentUserId);

  const [session, setSession] = useState<ChatSession>(() =>
    getCurrentSession(sessionKey),
  );
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    loadMessagesFromStorage(messagesKey),
  );
  const [input, setInput] = useState(
    () => localStorage.getItem(draftKey) || "",
  );
  const [, setToolResults] = useState<ToolResult[]>([]);
  const [voiceMode, setVoiceMode] = useState(false);
  const [handoverDialogOpen, setHandoverDialogOpen] = useState(false);
  const [handoverSubject, setHandoverSubject] = useState("");
  const [handoverPhone, setHandoverPhone] = useState("");
  const [handoverPriority, setHandoverPriority] = useState<
    "low" | "medium" | "high" | "urgent"
  >("medium");
  const [handoverSuccess, setHandoverSuccess] = useState(false);
  const [confirmationCode, setConfirmationCode] = useState("");
  const [lastResponseText, setLastResponseText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Get current user ID from localStorage
  const getCurrentUserId = (): number | undefined => {
    return currentUserId;
  };

  const chatMutation = useMutation({
    mutationFn: (messages: ChatMessage[]) =>
      api.chat(messages, getCurrentUserId(), voiceMode),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, data.message]);
      setToolResults(data.tool_results);
      // Update last response text for voice mode TTS
      if (voiceMode) {
        setLastResponseText(data.message.content);
      }
    },
  });

  const handoverMutation = useMutation({
    mutationFn: (data: {
      subject: string;
      phone: string | null;
      priority: string;
    }) =>
      api.requestHandover(messages, data.subject, data.phone, data.priority),
    onSuccess: (data) => {
      setHandoverSuccess(true);
      setConfirmationCode(data.confirmation_code);
    },
  });

  useEffect(() => {
    saveMessagesToStorage(messagesKey, messages);
    if (messages.length > 0) {
      updateSessionActivity(sessionKey, session);
    }
  }, [messages, session, messagesKey, sessionKey]);

  useEffect(() => {
    if (input) {
      localStorage.setItem(draftKey, input);
    } else {
      localStorage.removeItem(draftKey);
    }
  }, [input, draftKey]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden" && input) {
        localStorage.setItem(draftKey, input);
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [input, draftKey]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = { role: "user", content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    localStorage.removeItem(draftKey);

    chatMutation.mutate(updatedMessages);

    // Keep focus on the input after sending
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleHandoverClick = () => {
    if (messages.length === 0) {
      alert(
        "Please start a conversation first before requesting human assistance.",
      );
      return;
    }
    setHandoverDialogOpen(true);
    setHandoverSuccess(false);
  };

  const handleHandoverSubmit = () => {
    if (!handoverSubject.trim()) {
      alert("Please provide a subject for your request.");
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
    setHandoverSubject("");
    setHandoverPhone("");
    setHandoverPriority("medium");
    setHandoverSuccess(false);
    setConfirmationCode("");
  };

  // Voice mode handlers
  const handleVoiceTranscription = (text: string) => {
    const userMessage: ChatMessage = { role: "user", content: text };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    chatMutation.mutate(updatedMessages);
  };

  const handleSpeechToText = async (audioBlob: Blob): Promise<string> => {
    return await api.speechToText(audioBlob);
  };

  const handleTextToSpeech = async (text: string): Promise<Blob> => {
    return await api.textToSpeech(text);
  };

  // Reset lastResponseText after it's been used for TTS
  const handleVoiceResponseComplete = () => {
    setLastResponseText("");
    localStorage.removeItem(draftKey);
  };

  const handleNewSession = () => {
    if (messages.length > 0) {
      const confirmed = window.confirm(
        "Starting a new session will clear your current conversation. Are you sure?",
      );
      if (!confirmed) return;
    }

    const newSession = createNewSession(sessionKey);
    setSession(newSession);
    setMessages([]);
    setToolResults([]);
    setLastResponseText("");
    localStorage.removeItem(messagesKey);
    localStorage.removeItem(draftKey);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Scroll to bottom when switching modes
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [voiceMode]);

  return (
    <Box
      sx={{
        height: "calc(100vh - 120px)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Chat Container - Full Width */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          borderRadius: 2,
          border: "1px solid",
          borderColor: "divider",
          overflow: "hidden",
          bgcolor: "#fff",
        }}
      >
        {/* Header */}
        <Box
          sx={{
            px: 3,
            py: 1.5,
            borderBottom: "1px solid",
            borderColor: "divider",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            bgcolor: "#fff",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Typography
              variant="h6"
              sx={{ fontWeight: 600, color: "text.primary" }}
            >
              AI Assistant
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={<SupportAgentIcon sx={{ fontSize: 18 }} />}
              onClick={handleHandoverClick}
              disabled={messages.length === 0}
              sx={{
                textTransform: "none",
                fontWeight: 600,
                fontSize: "0.8125rem",
                borderColor: "#ed6c02",
                color: "#ed6c02",
                px: 2,
                py: 0.5,
                borderRadius: 2,
                "&:hover": {
                  bgcolor: alpha("#ed6c02", 0.08),
                  borderColor: "#ed6c02",
                },
                "&.Mui-disabled": {
                  borderColor: "#e0e0e0",
                  color: "text.disabled",
                },
              }}
            >
              Talk to a Human
            </Button>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            {/* Mode Tabs */}
            <Tabs
              value={voiceMode ? 1 : 0}
              onChange={(_, v) => setVoiceMode(v === 1)}
              sx={{
                minHeight: 36,
                "& .MuiTabs-indicator": {
                  bgcolor: "#840132",
                },
                "& .MuiTab-root": {
                  minHeight: 36,
                  py: 0,
                  px: 2,
                  fontSize: "0.8125rem",
                  fontWeight: 500,
                  textTransform: "none",
                  color: "text.secondary",
                  "&.Mui-selected": {
                    color: "#840132",
                  },
                },
              }}
            >
              <Tab
                icon={<KeyboardIcon sx={{ fontSize: 18 }} />}
                iconPosition="start"
                label="Text"
              />
              <Tab
                icon={<MicIcon sx={{ fontSize: 18 }} />}
                iconPosition="start"
                label="Voice"
              />
            </Tabs>

            <Box
              sx={{
                borderLeft: "1px solid",
                borderColor: "divider",
                height: 24,
              }}
            />

            <IconButton
              onClick={handleNewSession}
              size="small"
              title="New conversation"
              sx={{
                color: "text.secondary",
                "&:hover": { color: "#840132" },
              }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>

        {/* Voice Mode Panel */}
        {voiceMode && (
          <Box
            sx={{
              borderBottom: "1px solid",
              borderColor: "divider",
              bgcolor: "#fafbfc",
            }}
          >
            <VoiceChat
              onTranscription={handleVoiceTranscription}
              onSpeechToText={handleSpeechToText}
              onTextToSpeech={handleTextToSpeech}
              responseText={lastResponseText}
              isProcessing={chatMutation.isPending}
              onResponseComplete={handleVoiceResponseComplete}
            />
          </Box>
        )}

        {/* Messages Area - Scrollable */}
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 3,
            display: "flex",
            flexDirection: "column",
            gap: 2.5,
            bgcolor: "#fafbfc",
          }}
        >
          {/* Welcome State */}
          {messages.length === 0 && (
            <Box sx={{ py: 8, textAlign: "center" }}>
              <Typography
                variant="h6"
                sx={{ fontWeight: 600, color: "text.primary", mb: 1 }}
              >
                How can I help you today?
              </Typography>
              <Typography
                variant="body2"
                sx={{ color: "text.secondary", mb: 3 }}
              >
                {voiceMode
                  ? "Click the microphone to start speaking"
                  : "Ask me about appointments, providers, or lab tests"}
              </Typography>
            </Box>
          )}

          {/* Message List */}
          {messages.map((msg, idx) => (
            <Box
              key={idx}
              sx={{
                display: "flex",
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              <Box
                sx={{
                  maxWidth: "70%",
                  py: 1.5,
                  px: 2.5,
                  bgcolor: msg.role === "user" ? "#840132" : "#fff",
                  color: msg.role === "user" ? "#fff" : "text.primary",
                  borderRadius:
                    msg.role === "user"
                      ? "18px 18px 4px 18px"
                      : "18px 18px 18px 4px",
                  border: msg.role === "user" ? "none" : "1px solid",
                  borderColor: "divider",
                  "& p": { margin: "0.4em 0" },
                  "& p:first-of-type": { marginTop: 0 },
                  "& p:last-of-type": { marginBottom: 0 },
                  "& ul, & ol": { my: 0.5, pl: 2.5 },
                  "& li": { mb: 0.25 },
                }}
              >
                {msg.role === "user" ? (
                  <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                    {msg.content}
                  </Typography>
                ) : (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => (
                        <Typography
                          variant="body2"
                          component="p"
                          sx={{ lineHeight: 1.6 }}
                        >
                          {children}
                        </Typography>
                      ),
                      li: ({ children }) => (
                        <li>
                          <Typography variant="body2" component="span">
                            {children}
                          </Typography>
                        </li>
                      ),
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                )}
              </Box>
            </Box>
          ))}

          {/* Loading */}
          {chatMutation.isPending && (
            <Box sx={{ display: "flex", justifyContent: "flex-start" }}>
              <Box
                sx={{
                  py: 1.5,
                  px: 2.5,
                  bgcolor: "#fff",
                  borderRadius: "18px 18px 18px 4px",
                  border: "1px solid",
                  borderColor: "divider",
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                }}
              >
                <CircularProgress size={14} sx={{ color: "#840132" }} />
                <Typography variant="body2" sx={{ color: "text.secondary" }}>
                  Processing...
                </Typography>
              </Box>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area - Text Mode Only */}
        {!voiceMode && (
          <Box
            sx={{
              p: 2,
              borderTop: "1px solid",
              borderColor: "divider",
              bgcolor: "#fff",
            }}
          >
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              inputRef={inputRef}
              autoFocus
              onKeyPress={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              disabled={chatMutation.isPending}
              size="small"
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 2,
                  bgcolor: "#fafbfc",
                  "& fieldset": { borderColor: "divider" },
                  "&:hover fieldset": { borderColor: alpha("#840132", 0.3) },
                  "&.Mui-focused fieldset": { borderColor: "#840132" },
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={handleSend}
                      disabled={chatMutation.isPending || !input.trim()}
                      size="small"
                      sx={{
                        bgcolor: input.trim() ? "#840132" : "transparent",
                        color: input.trim() ? "#fff" : "text.disabled",
                        "&:hover": {
                          bgcolor: input.trim() ? "#6a0129" : "transparent",
                        },
                        "&.Mui-disabled": {
                          bgcolor: "transparent",
                          color: "text.disabled",
                        },
                      }}
                    >
                      <SendIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        )}
      </Paper>

      {/* Handover Dialog */}
      <Dialog
        open={handoverDialogOpen}
        onClose={handleHandoverClose}
        maxWidth="sm"
        fullWidth
      >
        {!handoverSuccess ? (
          <>
            <DialogTitle>Request Human Assistance</DialogTitle>
            <DialogContent>
              <DialogContentText>
                Our care team will review your conversation and contact you
                soon.
              </DialogContentText>
              <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
                <strong>For emergencies:</strong> Please call 911 immediately.
              </Alert>
              <TextField
                autoFocus
                margin="dense"
                label="Subject"
                fullWidth
                required
                value={handoverSubject}
                onChange={(e) => setHandoverSubject(e.target.value)}
                placeholder="Brief description of your request"
                sx={{ mb: 2 }}
              />
              <TextField
                margin="dense"
                label="Phone (Optional)"
                type="tel"
                fullWidth
                value={handoverPhone}
                onChange={(e) => setHandoverPhone(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <PhoneIcon
                      sx={{ mr: 1, color: "action.active", fontSize: 20 }}
                    />
                  ),
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
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </TextField>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleHandoverClose}>Cancel</Button>
              <Button
                onClick={handleHandoverSubmit}
                variant="contained"
                disabled={handoverMutation.isPending || !handoverSubject.trim()}
              >
                {handoverMutation.isPending ? "Submitting..." : "Submit"}
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
                Our team will contact you within 24 hours.
              </Typography>
              <Box sx={{ mt: 2, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
                <Typography variant="caption" sx={{ color: "text.secondary" }}>
                  Confirmation Code
                </Typography>
                <Typography variant="h6" color="primary">
                  {confirmationCode}
                </Typography>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleHandoverClose} variant="contained">
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}
