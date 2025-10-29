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

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

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
  async register(email: string, name: string, password: string): Promise<TokenResponse> {
    const { data } = await this.client.post<TokenResponse>('/auth/register', {
      email,
      name,
      password,
      role: 'patient',
    });
    localStorage.setItem('access_token', data.access_token);
    return data;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const { data } = await this.client.post<TokenResponse>('/auth/login', {
      email,
      password,
    });
    localStorage.setItem('access_token', data.access_token);
    return data;
  }

  logout(): void {
    localStorage.removeItem('access_token');
  }

  // Chat
  async chat(messages: ChatMessage[], userId?: number): Promise<ChatResponse> {
    const { data } = await this.client.post<ChatResponse>('/agent/chat', {
      messages,
      user_id: userId,
      stream: false,
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
    const { data } = await this.client.get<HealthMetrics>('/health');
    return data;
  }
}

export const api = new ApiClient();
