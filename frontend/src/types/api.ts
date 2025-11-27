/**
 * API client types
 */

export interface User {
  id: number;
  email: string;
  name: string;
  phone?: string | null;
  role: 'patient' | 'admin' | 'staff';
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Provider {
  id: number;
  name: string;
  department: string;
  type: string;
  specialty?: string;
  bio?: string;
  availability_calendar_id?: string;
  created_at: string;
}

export interface TimeSlot {
  slot_id: string;
  start: string;
  end: string;
  available: boolean;
}

export interface Appointment {
  id: number;
  user_id: number;
  provider_id: number;
  time_start: string;
  time_end: string;
  status: 'confirmed' | 'cancelled' | 'completed' | 'no_show';
  channel: 'web' | 'phone' | 'agent';
  reason?: string;
  notes?: string;
  confirmation_code?: string;
  created_at: string;
  updated_at: string;
}

export interface AppointmentWithDetails extends Appointment {
  user_name: string;
  user_email: string;
  provider_name: string;
  provider_department: string;
}

export interface LabTest {
  id: number;
  name: string;
  code: string;
  department: string;
  description?: string;
  prep_instructions?: string;
  fasting_hours?: number;
  estimated_duration_minutes: number;
  created_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, any>;
}

export interface ToolResult {
  tool_call_id: string;
  name: string;
  result: Record<string, any>;
  success: boolean;
  error?: string;
}

export interface ChatResponse {
  message: ChatMessage;
  tool_calls: ToolCall[];
  tool_results: ToolResult[];
  finish_reason: string;
  usage?: Record<string, number>;
  latency_ms: number;
}

export interface Document {
  title: string;
  content: string;
  metadata?: Record<string, string>;
  doc_type?: string;
}

export interface KPIResponse {
  task_completion_rate: number;
  avg_response_time_p50: number;
  avg_response_time_p90: number;
  avg_response_time_p99: number;
  ambiguity_success_rate: number;
  avg_satisfaction_score: number;
  total_conversations: number;
  period_start: string;
  period_end: string;
}

export interface HealthMetrics {
  status: string;
  uptime_seconds: number;
  database_connected: boolean;
  vector_store_loaded: boolean;
  openai_api_healthy: boolean;
  active_requests: number;
}
