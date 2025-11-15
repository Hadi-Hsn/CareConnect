/**
 * API client for CareConnect backend
 */
import axios, { AxiosInstance } from 'axios';
import type {
  User,
  TokenResponse,
  Provider,
  TimeSlot,
  Appointment,
  AppointmentWithDetails,
  LabTest,
  ChatMessage,
  ChatResponse,
  Document,
  KPIResponse,
  HealthMetrics,
} from '@/types/api';

// Support both VITE_API_BASE and VITE_API_BASE_URL (some deployments use the _URL name)
const API_BASE =
  (import.meta.env as any).VITE_API_BASE || (import.meta.env as any).VITE_API_BASE_URL ||
  'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth interceptor
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Auth
  async register(
    email: string,
    name: string,
    password: string,
    confirmPassword: string,
    phone?: string
  ): Promise<TokenResponse> {
    const { data } = await this.client.post<TokenResponse>('/auth/register', {
      email,
      name,
      password,
      confirm_password: confirmPassword,
      phone: phone || null,
      role: 'patient',
    });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const { data } = await this.client.post<TokenResponse>('/auth/login', {
      email,
      password,
    });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  }

  // Chat
  async chat(messages: ChatMessage[], userId?: number, voiceMode?: boolean): Promise<ChatResponse> {
    const { data } = await this.client.post<ChatResponse>('/agent/chat', {
      messages,
      user_id: userId,
      stream: false,
      voice_mode: voiceMode || false,
    });
    return data;
  }

  async submitFeedback(
    rating: number,
    thumbsUp: boolean,
    comment?: string,
    tags?: string[]
  ): Promise<void> {
    await this.client.post('/agent/feedback', {
      rating,
      thumbs_up: thumbsUp,
      comment,
      tags,
    });
  }

  // Providers
  async getProviders(filters?: {
    department?: string;
    provider_type?: string;
  }): Promise<Provider[]> {
    const { data } = await this.client.get<Provider[]>('/providers', { params: filters });
    return data;
  }

  async getProvider(id: number): Promise<Provider> {
    const { data } = await this.client.get<Provider>(`/providers/${id}`);
    return data;
  }

  async createProvider(provider: {
    name: string;
    type: string;
    department: string;
    specialty?: string | null;
    bio?: string | null;
    availability_calendar_id?: string | null;
  }): Promise<Provider> {
    const { data } = await this.client.post<Provider>('/providers', provider);
    return data;
  }

  async updateProvider(id: number, updates: {
    name?: string;
    type?: string;
    department?: string;
    specialty?: string | null;
    bio?: string | null;
    availability_calendar_id?: string | null;
  }): Promise<Provider> {
    const { data } = await this.client.patch<Provider>(`/providers/${id}`, updates);
    return data;
  }

  async deleteProvider(id: number): Promise<void> {
    await this.client.delete(`/providers/${id}`);
  }

  async getTimeslots(providerId: number, date: string): Promise<{ slots: TimeSlot[] }> {
    const { data } = await this.client.get(`/providers/${providerId}/timeslots`, {
      params: { date },
    });
    return data;
  }

  // Appointments
  async getAppointments(filters?: {
    user_id?: number;
    provider_id?: number;
  }): Promise<AppointmentWithDetails[]> {
    const { data } = await this.client.get<AppointmentWithDetails[]>('/appointments', {
      params: filters,
    });
    return data;
  }

  async getAppointment(id: number): Promise<AppointmentWithDetails> {
    const { data } = await this.client.get<AppointmentWithDetails>(`/appointments/${id}`);
    return data;
  }

  async createAppointment(appointment: {
    user_id: number;
    provider_id: number;
    time_start: string;
    time_end: string;
    reason?: string;
    channel?: string;
  }): Promise<Appointment> {
    const { data } = await this.client.post<Appointment>('/appointments', appointment);
    return data;
  }

  async updateAppointment(
    id: number,
    updates: {
      time_start?: string;
      time_end?: string;
      status?: string;
      reason?: string;
      notes?: string;
    }
  ): Promise<Appointment> {
    const { data } = await this.client.patch<Appointment>(`/appointments/${id}`, updates);
    return data;
  }

  async deleteAppointment(id: number): Promise<void> {
    await this.client.delete(`/appointments/${id}`);
  }

  // Lab Tests
  async getLabTests(filters?: { department?: string }): Promise<LabTest[]> {
    const { data } = await this.client.get<LabTest[]>('/labs', { params: filters });
    return data;
  }

  async getLabTest(id: number): Promise<LabTest> {
    const { data } = await this.client.get<LabTest>(`/labs/${id}`);
    return data;
  }

  // RAG/Admin
  async indexDocuments(documents: Document[], replace: boolean = false): Promise<any> {
    const { data } = await this.client.post('/rag/index', { documents, replace });
    return data;
  }

  // File uploads (PDF)
  async uploadPDF(file: File, doc_type: string = 'document', provider_id?: number): Promise<any> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('doc_type', doc_type);
    if (provider_id !== undefined && provider_id !== null) {
      formData.append('provider_id', String(provider_id));
    }

    const { data } = await this.client.post('/files/upload-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }

  async uploadGeneralDocument(file: File, doc_type: string = 'general'): Promise<any> {
    return this.uploadPDF(file, doc_type);
  }

  async getRAGStats(): Promise<any> {
    const { data } = await this.client.get('/rag/stats');
    return data;
  }

  // Metrics
  async getKPIs(days: number = 7): Promise<KPIResponse> {
    const { data } = await this.client.get<KPIResponse>('/eval/kpis', { params: { days } });
    return data;
  }

  async getHealth(): Promise<HealthMetrics> {
    const { data} = await this.client.get<HealthMetrics>('/health');
    return data;
  }

  // Cost Tracking
  async getCostSummary(): Promise<any> {
    const { data } = await this.client.get('/eval/cost/summary');
    return data;
  }

  async downloadCostLog(): Promise<Blob> {
    const { data } = await this.client.get('/eval/cost/download', {
      responseType: 'blob'
    });
    return data;
  }

  // Evaluation
  async getEvaluationReport(): Promise<any> {
    const { data } = await this.client.get('/eval/report');
    return data;
  }

  async runEvaluation(): Promise<any> {
    const { data } = await this.client.post('/admin/run-evaluation');
    return data;
  }

  // Handover
  async requestHandover(
    messages: ChatMessage[],
    subject: string,
    phone: string | null,
    priority: string
  ): Promise<{
    incident_id: number;
    status: string;
    message: string;
    confirmation_code: string;
    estimated_response_time: string;
  }> {
    const { data } = await this.client.post('/handover/request', {
      messages,
      subject,
      patient_phone: phone,
      priority,
    });
    return data;
  }

  async getIncidents(status?: string): Promise<any[]> {
    const { data } = await this.client.get('/handover/incidents', {
      params: { status },
    });
    return data;
  }

  async getIncident(id: number): Promise<any> {
    const { data } = await this.client.get(`/handover/incidents/${id}`);
    return data;
  }

  async updateIncident(id: number, updates: any): Promise<any> {
    const { data } = await this.client.patch(`/handover/incidents/${id}`, updates);
    return data;
  }

  async getIncidentStats(): Promise<any> {
    const { data } = await this.client.get('/handover/incidents/stats/overview');
    return data;
  }

  // Voice
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

    const { data } = await this.client.post<{ text: string }>('/voice/speech-to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data.text;
  }
}

export const api = new ApiClient();
