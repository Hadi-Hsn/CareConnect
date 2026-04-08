/**
 * API client for CareConnect backend
 */
import axios, { AxiosInstance } from "axios";
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
} from "@/types/api";

// Support both VITE_API_BASE and VITE_API_BASE_URL (some deployments use the _URL name)
const API_BASE =
  (import.meta.env as any).VITE_API_BASE ||
  (import.meta.env as any).VITE_API_BASE_URL ||
  "http://localhost:8000/api/v1";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add auth interceptor
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("access_token");
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
    phone: string,
    countryCode: string = "+961",
  ): Promise<TokenResponse> {
    const { data } = await this.client.post<TokenResponse>("/auth/register", {
      email,
      name,
      password,
      confirm_password: confirmPassword,
      phone: phone,
      country_code: countryCode,
      role: "patient",
    });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));
    return data;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const { data } = await this.client.post<TokenResponse>("/auth/login", {
      email,
      password,
    });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));
    return data;
  }

  logout(): void {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem("user");
    if (!userStr) return null;
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  }

  // Chat
  async chat(
    messages: ChatMessage[],
    userId?: number,
    voiceMode?: boolean,
  ): Promise<ChatResponse> {
    const { data } = await this.client.post<ChatResponse>("/agent/chat", {
      messages,
      user_id: userId,
      stream: false,
      voice_mode: voiceMode || false,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    });
    return data;
  }

  async submitFeedback(
    rating: number,
    thumbsUp: boolean,
    comment?: string,
    tags?: string[],
  ): Promise<void> {
    await this.client.post("/agent/feedback", {
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
    const { data } = await this.client.get<Provider[]>("/providers", {
      params: filters,
    });
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
    const { data } = await this.client.post<Provider>("/providers", provider);
    return data;
  }

  async updateProvider(
    id: number,
    updates: {
      name?: string;
      type?: string;
      department?: string;
      specialty?: string | null;
      bio?: string | null;
      availability_calendar_id?: string | null;
    },
  ): Promise<Provider> {
    const { data } = await this.client.patch<Provider>(
      `/providers/${id}`,
      updates,
    );
    return data;
  }

  async deleteProvider(id: number): Promise<void> {
    await this.client.delete(`/providers/${id}`);
  }

  async getTimeslots(
    providerId: number,
    date: string,
  ): Promise<{ slots: TimeSlot[] }> {
    const { data } = await this.client.get(
      `/providers/${providerId}/timeslots`,
      {
        params: { date },
      },
    );
    return data;
  }

  // Appointments
  async getAppointments(filters?: {
    user_id?: number;
    provider_id?: number;
  }): Promise<AppointmentWithDetails[]> {
    const { data } = await this.client.get<AppointmentWithDetails[]>(
      "/appointments",
      {
        params: filters,
      },
    );
    return data;
  }

  async getAppointment(id: number): Promise<AppointmentWithDetails> {
    const { data } = await this.client.get<AppointmentWithDetails>(
      `/appointments/${id}`,
    );
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
    const { data } = await this.client.post<Appointment>(
      "/appointments",
      appointment,
    );
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
    },
  ): Promise<Appointment> {
    const { data } = await this.client.patch<Appointment>(
      `/appointments/${id}`,
      updates,
    );
    return data;
  }

  async deleteAppointment(id: number): Promise<void> {
    await this.client.delete(`/appointments/${id}`);
  }

  async clearCancelledAppointments(userId?: number): Promise<void> {
    try {
      const config: any = {
        validateStatus: (status: number) =>
          status === 204 || (status >= 200 && status < 300),
      };

      // Only add user_id param if it's provided
      if (userId !== undefined && userId !== null) {
        config.params = { user_id: userId };
      }

      await this.client.delete("/appointments/clear-cancelled", config);

      // 204 No Content is a valid success response
      return;
    } catch (error: any) {
      console.error("API error in clearCancelledAppointments:", error);
      console.error("Error response:", error?.response);
      console.error("Error response data:", error?.response?.data);

      // Preserve the original error structure so the mutation can extract the message properly
      // Don't wrap it in a new Error, just re-throw the axios error
      throw error;
    }
  }

  // Lab Tests
  async getLabTests(filters?: { department?: string }): Promise<LabTest[]> {
    const { data } = await this.client.get<LabTest[]>("/labs", {
      params: filters,
    });
    return data;
  }

  async getLabTest(id: number): Promise<LabTest> {
    const { data } = await this.client.get<LabTest>(`/labs/${id}`);
    return data;
  }

  // RAG/Admin
  async indexDocuments(
    documents: Document[],
    replace: boolean = false,
  ): Promise<any> {
    const { data } = await this.client.post("/rag/index", {
      documents,
      replace,
    });
    return data;
  }

  // File uploads (PDF)
  async uploadPDF(
    file: File,
    doc_type: string = "document",
    provider_id?: number,
  ): Promise<any> {
    const formData = new FormData();
    formData.append("file", file, file.name);
    formData.append("doc_type", doc_type);
    if (provider_id !== undefined && provider_id !== null) {
      formData.append("provider_id", String(provider_id));
    }

    const { data } = await this.client.post("/files/upload-pdf", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  }

  async uploadGeneralDocument(
    file: File,
    doc_type: string = "general",
  ): Promise<any> {
    return this.uploadPDF(file, doc_type);
  }

  async getRAGStats(): Promise<any> {
    const { data } = await this.client.get("/rag/stats");
    return data;
  }

  // Metrics
  async getKPIs(days: number = 7): Promise<KPIResponse> {
    const { data } = await this.client.get<KPIResponse>("/eval/kpis", {
      params: { days },
    });
    return data;
  }

  async getHealth(): Promise<HealthMetrics> {
    const { data } = await this.client.get<HealthMetrics>("/health");
    return data;
  }

  // Cost Tracking
  async getCostSummary(): Promise<any> {
    const { data } = await this.client.get("/eval/cost/summary");
    return data;
  }

  async downloadCostLog(): Promise<Blob> {
    const { data } = await this.client.get("/eval/cost/download", {
      responseType: "blob",
    });
    return data;
  }

  // Evaluation
  async getEvaluationReport(): Promise<any> {
    const { data } = await this.client.get("/eval/report");
    return data;
  }

  async runEvaluation(): Promise<any> {
    const { data } = await this.client.post("/admin/run-evaluation");
    return data;
  }

  // Handover
  async requestHandover(
    messages: ChatMessage[],
    subject: string,
    phone: string | null,
    priority: string,
  ): Promise<{
    incident_id: number;
    status: string;
    message: string;
    confirmation_code: string;
    estimated_response_time: string;
  }> {
    const { data } = await this.client.post("/handover/request", {
      messages,
      subject,
      patient_phone: phone,
      priority,
    });
    return data;
  }

  async getIncidents(status?: string): Promise<any[]> {
    const { data } = await this.client.get("/handover/incidents", {
      params: { status },
    });
    return data;
  }

  async getIncident(id: number): Promise<any> {
    const { data } = await this.client.get(`/handover/incidents/${id}`);
    return data;
  }

  async updateIncident(id: number, updates: any): Promise<any> {
    const { data } = await this.client.patch(
      `/handover/incidents/${id}`,
      updates,
    );
    return data;
  }

  async getIncidentStats(): Promise<any> {
    const { data } = await this.client.get(
      "/handover/incidents/stats/overview",
    );
    return data;
  }

  // Patients (Admin)
  async getPatients(search?: string): Promise<any[]> {
    const { data } = await this.client.get("/admin/patients", {
      params: { search, limit: 100 },
    });
    return data;
  }

  async getPatientDetails(id: number): Promise<any> {
    const { data } = await this.client.get(`/admin/patients/${id}`);
    return data;
  }

  async updatePatient(
    id: number,
    updates: {
      name?: string;
      email?: string;
      phone?: string;
    },
  ): Promise<any> {
    const { data } = await this.client.put(`/admin/patients/${id}`, updates);
    return data;
  }

  async deletePatient(id: number): Promise<void> {
    await this.client.delete(`/admin/patients/${id}`);
  }

  // Provider PDF Download
  async downloadProviderPDF(id: number): Promise<Blob> {
    const { data } = await this.client.get(
      `/admin/doctors/${id}/download-profile`,
      {
        responseType: "blob",
      },
    );
    return data;
  }

  // Hospital Documents
  async listDocuments(): Promise<any[]> {
    const { data } = await this.client.get("/rag/documents");
    return data;
  }

  async deleteDocument(docId: string): Promise<void> {
    await this.client.delete(`/rag/documents/${docId}`);
  }

  // Voice
  async textToSpeech(text: string, voice?: string): Promise<Blob> {
    const { data } = await this.client.post(
      "/voice/text-to-speech",
      { text, voice },
      { responseType: "blob" },
    );
    return data;
  }

  async speechToText(
    audioBlob: Blob,
    language: string = "en",
  ): Promise<string> {
    const formData = new FormData();
    formData.append("audio", audioBlob, "audio.webm");
    formData.append("language", language);

    const { data } = await this.client.post<{ text: string }>(
      "/voice/speech-to-text",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return data.text;
  }

  // Test Results (Admin)
  async getTestResultsAdmin(userId?: number, status?: string): Promise<any[]> {
    const { data } = await this.client.get("/test-results/admin/results", {
      params: { user_id: userId, status_filter: status },
    });
    return data;
  }

  async createTestResult(resultData: {
    user_id: number;
    test_name: string;
    test_category: string;
    test_date: string;
    result_value?: string;
    result_unit?: string;
    reference_range?: string;
    status: string;
    notes?: string;
    ordered_by_provider_id?: number;
  }): Promise<any> {
    const { data } = await this.client.post(
      "/test-results/admin/results",
      resultData,
    );
    return data;
  }

  async uploadTestResultPdf(resultId: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file, file.name);

    const { data } = await this.client.post(
      `/test-results/admin/results/${resultId}/upload-pdf`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return data;
  }

  async createTestResultWithPdf(
    userId: number,
    testName: string,
    testDate: string,
    file: File,
    options?: {
      test_category?: string;
      result_value?: string;
      result_unit?: string;
      reference_range?: string;
      notes?: string;
      ordered_by_provider_id?: number;
    },
  ): Promise<any> {
    const formData = new FormData();
    formData.append("user_id", String(userId));
    formData.append("test_name", testName);
    formData.append("test_date", testDate);
    formData.append("file", file, file.name);

    if (options?.test_category)
      formData.append("test_category", options.test_category);
    if (options?.result_value)
      formData.append("result_value", options.result_value);
    if (options?.result_unit)
      formData.append("result_unit", options.result_unit);
    if (options?.reference_range)
      formData.append("reference_range", options.reference_range);
    if (options?.notes) formData.append("notes", options.notes);
    if (options?.ordered_by_provider_id)
      formData.append(
        "ordered_by_provider_id",
        String(options.ordered_by_provider_id),
      );

    const { data } = await this.client.post(
      "/test-results/admin/results/upload-with-pdf",
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return data;
  }

  async deleteTestResult(resultId: number): Promise<void> {
    await this.client.delete(`/test-results/admin/results/${resultId}`);
  }

  // Test Results (Patient)
  async getMyTestResults(filters?: {
    status_filter?: string;
    category?: string;
  }): Promise<any[]> {
    const { data } = await this.client.get("/test-results/my-results", {
      params: filters,
    });
    return data;
  }

  async getMyTestResultCategories(): Promise<string[]> {
    const { data } = await this.client.get(
      "/test-results/my-results/categories/list",
    );
    return data;
  }

  async downloadMyTestResultPdf(resultId: number): Promise<Blob> {
    const response = await this.client.get(
      `/test-results/my-results/${resultId}/pdf`,
      {
        responseType: "blob",
      },
    );
    return response.data;
  }
}

export const api = new ApiClient();
