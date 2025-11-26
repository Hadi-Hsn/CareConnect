/**
 * Patients Management Page
 * Professional admin interface for managing patient records
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Tooltip,
  Grid,
  Avatar,
  Divider,
  alpha,
} from '@mui/material';
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Person as PersonIcon,
  Event as EventIcon,
  Science as ScienceIcon,
  CalendarMonth as CalendarIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

const BRAND_COLOR = '#840132';

interface Patient {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  created_at: string;
  total_appointments: number;
  upcoming_appointments: number;
  total_test_results: number;
}

interface PatientDetails {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  created_at: string;
  appointments: Array<{
    id: number;
    provider_name: string;
    provider_department: string;
    time_start: string;
    time_end: string;
    status: string;
    reason: string;
    notes: string | null;
    confirmation_code: string;
  }>;
  test_results: Array<{
    id: number;
    test_name: string;
    test_code: string;
    test_date: string;
    result_value: string;
    result_unit: string;
    reference_range: string;
    status: string;
    notes: string | null;
    ordered_by: string | null;
  }>;
}

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<PatientDetails | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editForm, setEditForm] = useState({ name: '', email: '', phone: '' });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPatients();
  }, [searchTerm]);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getPatients(searchTerm);
      setPatients(response);
    } catch (err: any) {
      setError(err.message || 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const fetchPatientDetails = async (patientId: number) => {
    try {
      setLoading(true);
      const response = await api.getPatientDetails(patientId);
      setSelectedPatient(response);
      setViewDialogOpen(true);
    } catch (err: any) {
      setError(err.message || 'Failed to load patient details');
    } finally {
      setLoading(false);
    }
  };

  const handleEditOpen = (patient: Patient) => {
    setEditForm({
      name: patient.name,
      email: patient.email,
      phone: patient.phone || '',
    });
    setSelectedPatient({
      ...patient,
      appointments: [],
      test_results: [],
    });
    setEditDialogOpen(true);
  };

  const handleEditSubmit = async () => {
    if (!selectedPatient) return;

    try {
      setSubmitting(true);
      setError(null);
      await api.updatePatient(selectedPatient.id, editForm);
      await fetchPatients();
      setEditDialogOpen(false);
      setSelectedPatient(null);
    } catch (err: any) {
      setError(err.message || 'Failed to update patient');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedPatient) return;

    try {
      setSubmitting(true);
      setError(null);
      await api.deletePatient(selectedPatient.id);
      await fetchPatients();
      setDeleteDialogOpen(false);
      setSelectedPatient(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete patient');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return { bg: alpha('#2e7d32', 0.1), color: '#2e7d32' };
      case 'scheduled': return { bg: alpha('#1976d2', 0.1), color: '#1976d2' };
      case 'cancelled': return { bg: alpha('#d32f2f', 0.1), color: '#d32f2f' };
      case 'pending': return { bg: alpha('#ed6c02', 0.1), color: '#ed6c02' };
      default: return { bg: alpha('#666', 0.1), color: '#666' };
    }
  };

  // Stats calculations
  const stats = {
    total: patients.length,
    withAppointments: patients.filter(p => p.total_appointments > 0).length,
    upcomingAppointments: patients.reduce((sum, p) => sum + p.upcoming_appointments, 0),
    withLabTests: patients.filter(p => p.total_test_results > 0).length,
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 800,
            background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1,
          }}
        >
          Patient Management
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          View and manage patient records, appointments, and lab results
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {[
          { label: 'Total Patients', value: stats.total, color: '#840132', icon: <PersonIcon /> },
          { label: 'With Appointments', value: stats.withAppointments, color: '#1976d2', icon: <EventIcon /> },
          { label: 'Upcoming Visits', value: stats.upcomingAppointments, color: '#2e7d32', icon: <CalendarIcon /> },
          { label: 'With Lab Tests', value: stats.withLabTests, color: '#ed6c02', icon: <ScienceIcon /> },
        ].map((stat) => (
          <Grid item xs={6} md={3} key={stat.label}>
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'divider',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <Avatar sx={{ bgcolor: alpha(stat.color, 0.1), color: stat.color }}>
                {stat.icon}
              </Avatar>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>
                  {stat.value}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                  {stat.label}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Search Bar */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
        <TextField
          fullWidth
          placeholder="Search patients by name or email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#999' }} />
              </InputAdornment>
            ),
            sx: { borderRadius: 2 },
          }}
        />
      </Paper>

      {/* Patients Table */}
      <Paper sx={{ borderRadius: 3, overflow: 'hidden', border: '1px solid', borderColor: 'divider' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: alpha(BRAND_COLOR, 0.03) }}>
                <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }}>Patient</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }}>Contact</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }}>Registered</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }} align="center">Appointments</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }} align="center">Lab Tests</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }} align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 8 }}>
                    <CircularProgress sx={{ color: BRAND_COLOR }} />
                  </TableCell>
                </TableRow>
              ) : patients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 8 }}>
                    <PersonIcon sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
                    <Typography sx={{ color: '#666' }}>No patients found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                patients.map((patient) => (
                  <TableRow key={patient.id} hover sx={{ '&:hover': { bgcolor: alpha(BRAND_COLOR, 0.02) } }}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar
                          sx={{
                            bgcolor: alpha(BRAND_COLOR, 0.1),
                            color: BRAND_COLOR,
                            fontWeight: 600,
                          }}
                        >
                          {patient.name.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: '#1a1a1a' }}>
                            {patient.name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666' }}>
                            ID: #{patient.id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <EmailIcon sx={{ fontSize: 14, color: '#999' }} />
                          <Typography variant="body2" sx={{ color: '#1a1a1a' }}>
                            {patient.email}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <PhoneIcon sx={{ fontSize: 14, color: '#999' }} />
                          <Typography variant="body2" sx={{ color: patient.phone ? '#1a1a1a' : '#999' }}>
                            {patient.phone || 'Not provided'}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: '#1a1a1a' }}>
                        {formatDate(patient.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        <Chip
                          label={patient.total_appointments}
                          size="small"
                          sx={{
                            bgcolor: alpha(BRAND_COLOR, 0.1),
                            color: BRAND_COLOR,
                            fontWeight: 600,
                            minWidth: 32,
                          }}
                        />
                        {patient.upcoming_appointments > 0 && (
                          <Chip
                            label={`${patient.upcoming_appointments} upcoming`}
                            size="small"
                            sx={{
                              bgcolor: alpha('#2e7d32', 0.1),
                              color: '#2e7d32',
                              fontWeight: 600,
                            }}
                          />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={patient.total_test_results}
                        size="small"
                        sx={{
                          bgcolor: alpha('#1976d2', 0.1),
                          color: '#1976d2',
                          fontWeight: 600,
                          minWidth: 32,
                        }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => fetchPatientDetails(patient.id)}
                          sx={{ color: BRAND_COLOR }}
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Patient">
                        <IconButton
                          size="small"
                          onClick={() => handleEditOpen(patient)}
                          sx={{ color: '#666' }}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Patient">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedPatient({
                              ...patient,
                              appointments: [],
                              test_results: [],
                            });
                            setDeleteDialogOpen(true);
                          }}
                          sx={{ color: '#d32f2f' }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* View Patient Details Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        {selectedPatient && (
          <>
            <DialogTitle sx={{ pb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar
                  sx={{
                    bgcolor: alpha(BRAND_COLOR, 0.1),
                    color: BRAND_COLOR,
                    width: 56,
                    height: 56,
                    fontWeight: 600,
                    fontSize: 24,
                  }}
                >
                  {selectedPatient.name.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {selectedPatient.name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    Patient ID: #{selectedPatient.id}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              {/* Patient Info Card */}
              <Paper
                sx={{
                  p: 2.5,
                  mb: 3,
                  borderRadius: 2,
                  bgcolor: alpha(BRAND_COLOR, 0.03),
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" sx={{ color: '#666' }}>Email</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedPatient.email}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" sx={{ color: '#666' }}>Phone</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {selectedPatient.phone || 'Not provided'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" sx={{ color: '#666' }}>Registered</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {formatDate(selectedPatient.created_at)}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>

              {/* Appointments Section */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <EventIcon sx={{ color: BRAND_COLOR }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Appointments ({selectedPatient.appointments.length})
                  </Typography>
                </Box>
                {selectedPatient.appointments.length === 0 ? (
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: '#fafafa', borderRadius: 2 }}>
                    <Typography variant="body2" sx={{ color: '#666' }}>
                      No appointments
                    </Typography>
                  </Paper>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                    {selectedPatient.appointments.map((appt) => {
                      const statusStyle = getStatusColor(appt.status);
                      return (
                        <Paper
                          key={appt.id}
                          sx={{
                            p: 2,
                            borderRadius: 2,
                            border: '1px solid',
                            borderColor: 'divider',
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {appt.provider_name}
                            </Typography>
                            <Chip
                              label={appt.status}
                              size="small"
                              sx={{
                                bgcolor: statusStyle.bg,
                                color: statusStyle.color,
                                fontWeight: 600,
                                textTransform: 'capitalize',
                              }}
                            />
                          </Box>
                          <Typography variant="caption" sx={{ color: '#666' }}>
                            {appt.provider_department}
                          </Typography>
                          <Divider sx={{ my: 1 }} />
                          <Grid container spacing={1}>
                            <Grid item xs={6}>
                              <Typography variant="caption" sx={{ color: '#666' }}>Date & Time</Typography>
                              <Typography variant="body2">{formatDateTime(appt.time_start)}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" sx={{ color: '#666' }}>Confirmation</Typography>
                              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                {appt.confirmation_code}
                              </Typography>
                            </Grid>
                            <Grid item xs={12}>
                              <Typography variant="caption" sx={{ color: '#666' }}>Reason</Typography>
                              <Typography variant="body2">{appt.reason}</Typography>
                            </Grid>
                          </Grid>
                        </Paper>
                      );
                    })}
                  </Box>
                )}
              </Box>

              {/* Lab Test Results Section */}
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <ScienceIcon sx={{ color: BRAND_COLOR }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Lab Test Results ({selectedPatient.test_results.length})
                  </Typography>
                </Box>
                {selectedPatient.test_results.length === 0 ? (
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: '#fafafa', borderRadius: 2 }}>
                    <Typography variant="body2" sx={{ color: '#666' }}>
                      No test results
                    </Typography>
                  </Paper>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                    {selectedPatient.test_results.map((test) => {
                      const statusStyle = getStatusColor(test.status);
                      return (
                        <Paper
                          key={test.id}
                          sx={{
                            p: 2,
                            borderRadius: 2,
                            border: '1px solid',
                            borderColor: 'divider',
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {test.test_name}
                              </Typography>
                              <Typography variant="caption" sx={{ color: '#666' }}>
                                {test.test_code}
                              </Typography>
                            </Box>
                            <Chip
                              label={test.status}
                              size="small"
                              sx={{
                                bgcolor: statusStyle.bg,
                                color: statusStyle.color,
                                fontWeight: 600,
                                textTransform: 'capitalize',
                              }}
                            />
                          </Box>
                          <Divider sx={{ my: 1 }} />
                          <Grid container spacing={1}>
                            <Grid item xs={6}>
                              <Typography variant="caption" sx={{ color: '#666' }}>Result</Typography>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {test.result_value} {test.result_unit}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" sx={{ color: '#666' }}>Reference Range</Typography>
                              <Typography variant="body2">{test.reference_range}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" sx={{ color: '#666' }}>Test Date</Typography>
                              <Typography variant="body2">{formatDate(test.test_date)}</Typography>
                            </Grid>
                            {test.ordered_by && (
                              <Grid item xs={6}>
                                <Typography variant="caption" sx={{ color: '#666' }}>Ordered By</Typography>
                                <Typography variant="body2">{test.ordered_by}</Typography>
                              </Grid>
                            )}
                          </Grid>
                        </Paper>
                      );
                    })}
                  </Box>
                )}
              </Box>
            </DialogContent>
            <DialogActions sx={{ px: 3, py: 2 }}>
              <Button onClick={() => setViewDialogOpen(false)} sx={{ textTransform: 'none' }}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Edit Patient Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>Edit Patient</DialogTitle>
        <DialogContent dividers>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            <TextField
              label="Full Name"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              fullWidth
              required
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            />
            <TextField
              label="Email"
              type="email"
              value={editForm.email}
              onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
              fullWidth
              required
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            />
            <TextField
              label="Phone"
              value={editForm.phone}
              onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
              fullWidth
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setEditDialogOpen(false)} disabled={submitting} sx={{ textTransform: 'none' }}>
            Cancel
          </Button>
          <Button
            onClick={handleEditSubmit}
            variant="contained"
            disabled={submitting || !editForm.name || !editForm.email}
            sx={{
              bgcolor: BRAND_COLOR,
              '&:hover': { bgcolor: '#5e0124' },
              textTransform: 'none',
              borderRadius: 2,
              fontWeight: 600,
              px: 3,
            }}
          >
            {submitting ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>Delete Patient</DialogTitle>
        <DialogContent>
          <Typography sx={{ color: '#666' }}>
            Are you sure you want to delete this patient? This will also remove all associated
            appointments and test results. <strong>This action cannot be undone.</strong>
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={submitting} sx={{ textTransform: 'none' }}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            disabled={submitting}
            sx={{ textTransform: 'none', borderRadius: 2, fontWeight: 600 }}
          >
            {submitting ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
