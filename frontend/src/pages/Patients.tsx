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
} from '@mui/material';
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Person as PersonIcon,
  Event as EventIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

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

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: '#000000' }}>
          Patient Management
        </Typography>
        <Typography variant="body2" sx={{ color: '#808080' }}>
          View and manage patient information
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search Bar */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
        <TextField
          fullWidth
          placeholder="Search patients by name or email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#808080' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            },
          }}
        />
      </Paper>

      {/* Patients Table */}
      <Paper sx={{ borderRadius: 3, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: 'rgba(132, 1, 50, 0.04)' }}>
                <TableCell sx={{ fontWeight: 700 }}>Patient</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Contact</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Registered</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="center">
                  Appointments
                </TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="center">
                  Lab Tests
                </TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 8 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : patients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 8, color: '#808080' }}>
                    No patients found
                  </TableCell>
                </TableRow>
              ) : (
                patients.map((patient) => (
                  <TableRow key={patient.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PersonIcon sx={{ color: '#840132' }} />
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {patient.name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#808080' }}>
                            ID: {patient.id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{patient.email}</Typography>
                      <Typography variant="caption" sx={{ color: '#808080' }}>
                        {patient.phone || 'No phone'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{formatDate(patient.created_at)}</Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <Chip
                          label={patient.total_appointments}
                          size="small"
                          sx={{ bgcolor: 'rgba(132, 1, 50, 0.1)', color: '#840132', fontWeight: 600 }}
                        />
                        {patient.upcoming_appointments > 0 && (
                          <Chip
                            label={`${patient.upcoming_appointments} upcoming`}
                            size="small"
                            color="success"
                            sx={{ fontWeight: 600 }}
                          />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={patient.total_test_results}
                        size="small"
                        sx={{ bgcolor: 'rgba(0, 0, 0, 0.08)', fontWeight: 600 }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => fetchPatientDetails(patient.id)}
                          sx={{ color: '#840132' }}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Patient">
                        <IconButton
                          size="small"
                          onClick={() => handleEditOpen(patient)}
                          sx={{ color: '#000000' }}
                        >
                          <EditIcon />
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
                          <DeleteIcon />
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
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Patient Details
          </Typography>
        </DialogTitle>
        <DialogContent dividers>
          {selectedPatient && (
            <Box>
              {/* Patient Info */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'rgba(132, 1, 50, 0.04)', borderRadius: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">
                      Name
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {selectedPatient.name}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">
                      Email
                    </Typography>
                    <Typography variant="body1">{selectedPatient.email}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">
                      Phone
                    </Typography>
                    <Typography variant="body1">
                      {selectedPatient.phone || 'Not provided'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">
                      Registered
                    </Typography>
                    <Typography variant="body1">{formatDate(selectedPatient.created_at)}</Typography>
                  </Grid>
                </Grid>
              </Paper>

              {/* Appointments */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <EventIcon /> Appointments ({selectedPatient.appointments.length})
                </Typography>
                {selectedPatient.appointments.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No appointments
                  </Typography>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {selectedPatient.appointments.map((appt) => (
                      <Paper key={appt.id} sx={{ p: 2, borderRadius: 2 }}>
                        <Grid container spacing={1}>
                          <Grid item xs={12}>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {appt.provider_name} - {appt.provider_department}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Date & Time
                            </Typography>
                            <Typography variant="body2">{formatDateTime(appt.time_start)}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Status
                            </Typography>
                            <Typography variant="body2">
                              <Chip label={appt.status} size="small" />
                            </Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="caption" color="text.secondary">
                              Reason
                            </Typography>
                            <Typography variant="body2">{appt.reason}</Typography>
                          </Grid>
                        </Grid>
                      </Paper>
                    ))}
                  </Box>
                )}
              </Box>

              {/* Lab Test Results */}
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ScienceIcon /> Lab Test Results ({selectedPatient.test_results.length})
                </Typography>
                {selectedPatient.test_results.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No test results
                  </Typography>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {selectedPatient.test_results.map((test) => (
                      <Paper key={test.id} sx={{ p: 2, borderRadius: 2 }}>
                        <Grid container spacing={1}>
                          <Grid item xs={12}>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {test.test_name} ({test.test_code})
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Test Date
                            </Typography>
                            <Typography variant="body2">{formatDate(test.test_date)}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Result
                            </Typography>
                            <Typography variant="body2">
                              {test.result_value} {test.result_unit}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Reference Range
                            </Typography>
                            <Typography variant="body2">{test.reference_range}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Status
                            </Typography>
                            <Typography variant="body2">
                              <Chip label={test.status} size="small" />
                            </Typography>
                          </Grid>
                          {test.ordered_by && (
                            <Grid item xs={12}>
                              <Typography variant="caption" color="text.secondary">
                                Ordered By
                              </Typography>
                              <Typography variant="body2">{test.ordered_by}</Typography>
                            </Grid>
                          )}
                        </Grid>
                      </Paper>
                    ))}
                  </Box>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Patient Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Patient</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Name"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Email"
              type="email"
              value={editForm.email}
              onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Phone"
              value={editForm.phone}
              onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button
            onClick={handleEditSubmit}
            variant="contained"
            disabled={submitting || !editForm.name || !editForm.email}
            sx={{
              bgcolor: '#840132',
              '&:hover': { bgcolor: '#5e0124' },
            }}
          >
            {submitting ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="xs">
        <DialogTitle>Delete Patient</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this patient? This action cannot be undone and will also
            delete all associated appointments and test results.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            disabled={submitting}
          >
            {submitting ? <CircularProgress size={24} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
