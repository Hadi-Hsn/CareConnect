import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  alpha,
  Avatar,
  Fade,
  Tooltip,
  InputAdornment,
  Snackbar,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Schedule as ScheduleIcon,
  Event as EventIcon,
  AccessTime as TimeIcon,
  CalendarMonth as CalendarIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  ConfirmationNumber as ConfirmationIcon,
  MedicalServices as MedicalIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

// Helper function to format datetime in Lebanon timezone
const formatLebanonTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    timeZone: 'Asia/Beirut',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};

const formatLebanonDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    timeZone: 'Asia/Beirut',
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
};

const formatLebanonTimeOnly = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    timeZone: 'Asia/Beirut',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};

// Status configuration
const statusConfig: { [key: string]: { color: string; bgColor: string; icon: React.ReactElement; label: string } } = {
  confirmed: { color: '#2e7d32', bgColor: '#e8f5e9', icon: <CheckIcon fontSize="small" />, label: 'Confirmed' },
  cancelled: { color: '#d32f2f', bgColor: '#ffebee', icon: <CancelIcon fontSize="small" />, label: 'Cancelled' },
  completed: { color: '#1976d2', bgColor: '#e3f2fd', icon: <CheckIcon fontSize="small" />, label: 'Completed' },
  no_show: { color: '#757575', bgColor: '#f5f5f5', icon: <CancelIcon fontSize="small" />, label: 'No Show' },
};

// Appointment Card for Patient View
function AppointmentCard({ appointment, index }: { appointment: any; index: number }) {
  const status = statusConfig[appointment.status] || statusConfig.confirmed;
  
  return (
    <Fade in timeout={300 + index * 100}>
      <Card
        elevation={0}
        sx={{
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(0,0,0,0.1)',
            borderColor: 'transparent',
          },
        }}
      >
        {/* Status Bar */}
        <Box
          sx={{
            height: 4,
            background: `linear-gradient(90deg, ${status.color} 0%, ${alpha(status.color, 0.6)} 100%)`,
          }}
        />
        
        <CardContent sx={{ p: 3 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar
                sx={{
                  width: 56,
                  height: 56,
                  bgcolor: alpha('#840132', 0.1),
                  color: '#840132',
                }}
              >
                <MedicalIcon />
              </Avatar>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary', lineHeight: 1.2 }}>
                  {appointment.provider_name}
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  {appointment.provider_department}
                </Typography>
              </Box>
            </Box>
            <Chip
              icon={status.icon}
              label={status.label}
              size="small"
              sx={{
                bgcolor: status.bgColor,
                color: status.color,
                fontWeight: 600,
                '& .MuiChip-icon': { color: status.color },
              }}
            />
          </Box>
          
          {/* Appointment Details */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 2,
              p: 2,
              bgcolor: '#f8f9fa',
              borderRadius: 2,
              mb: 2,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <CalendarIcon sx={{ color: '#840132', fontSize: 20 }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.65rem' }}>
                  Date
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {formatLebanonDate(appointment.time_start)}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <TimeIcon sx={{ color: '#840132', fontSize: 20 }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.65rem' }}>
                  Time
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {formatLebanonTimeOnly(appointment.time_start)}
                </Typography>
              </Box>
            </Box>
          </Box>
          
          {/* Reason */}
          {appointment.reason && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.65rem' }}>
                Reason for Visit
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.primary', mt: 0.5 }}>
                {appointment.reason}
              </Typography>
            </Box>
          )}
          
          {/* Confirmation Code */}
          {appointment.confirmation_code && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                p: 1.5,
                bgcolor: alpha('#840132', 0.05),
                borderRadius: 2,
                border: '1px dashed',
                borderColor: alpha('#840132', 0.2),
              }}
            >
              <ConfirmationIcon sx={{ color: '#840132', fontSize: 18 }} />
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#840132' }}>
                Confirmation: {appointment.confirmation_code}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Fade>
  );
}

export default function AppointmentsPage() {
  const currentUser = api.getCurrentUser();
  const isAdmin = currentUser?.role === 'admin' || currentUser?.role === 'staff';
  
  const [selectedAppointment, setSelectedAppointment] = useState<any>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [timeSlotsDialogOpen, setTimeSlotsDialogOpen] = useState(false);
  const [clearCancelledDialogOpen, setClearCancelledDialogOpen] = useState(false);
  const [errorSnackbar, setErrorSnackbar] = useState({ open: false, message: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Edit form state
  const [editStatus, setEditStatus] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [editProviderId, setEditProviderId] = useState<number>(0);
  const [editDate, setEditDate] = useState('');
  const [editTimeStart, setEditTimeStart] = useState('');
  const [editTimeEnd, setEditTimeEnd] = useState('');
  
  // Time slots state
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedProviderId, setSelectedProviderId] = useState<number>(0);

  const queryClient = useQueryClient();

  // Fetch appointments
  const { data: appointments, isLoading, refetch: refetchAppointments } = useQuery({
    queryKey: ['appointments', isAdmin],
    queryFn: () => isAdmin ? api.getAppointments() : api.getAppointments({ user_id: currentUser?.id }),
  });
  const clearCancelledMutation = useMutation({
    mutationFn: async () => {
      try {
        const userId = isAdmin ? undefined : (currentUser?.id ?? undefined);
        await api.clearCancelledAppointments(userId);
      } catch (error: any) {
        console.error('Error in clearCancelledAppointments:', error);
        throw error;
      }
    },
    onSuccess: async () => {
      try {
        setClearCancelledDialogOpen(false);
        // Refetch appointments to get updated list
        try {
          await refetchAppointments();
        } catch (refetchError) {
          console.error('Error refetching appointments:', refetchError);
          // Still invalidate to trigger a refetch on next render
          queryClient.invalidateQueries({ queryKey: ['appointments'] });
        }
      } catch (error) {
        console.error('Error in onSuccess:', error);
        setErrorSnackbar({
          open: true,
          message: 'Appointments cleared, but there was an error refreshing. Please refresh the page.',
        });
      }
    },
    onError: (error: any) => {
      console.error('Failed to clear cancelled appointments - full error:', error);
      console.error('Error type:', typeof error);
      console.error('Error keys:', error ? Object.keys(error) : 'no error');
      if (error?.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
      }
      
      setClearCancelledDialogOpen(false);
      
      // Extract error message properly - handle all possible error structures
      let errorMessage = 'Failed to clear cancelled appointments. Please try again.';
      
      try {
        if (!error) {
          errorMessage = 'Unknown error occurred';
        } else if (typeof error === 'string') {
          errorMessage = error;
        } else if (error?.message) {
          if (typeof error.message === 'string') {
            errorMessage = error.message;
          } else {
            errorMessage = String(error.message);
          }
        } else if (error?.response) {
          const responseData = error.response.data;
          if (typeof responseData === 'string') {
            errorMessage = responseData;
          } else if (responseData?.detail) {
            errorMessage = typeof responseData.detail === 'string' 
              ? responseData.detail 
              : String(responseData.detail);
          } else if (responseData?.message) {
            errorMessage = typeof responseData.message === 'string'
              ? responseData.message
              : String(responseData.message);
          } else if (Array.isArray(responseData)) {
            errorMessage = responseData.map((item: any) => {
              if (typeof item === 'string') return item;
              if (item?.msg) return item.msg;
              if (item?.message) return item.message;
              return JSON.stringify(item);
            }).join(', ');
          } else if (typeof responseData === 'object') {
            // Try to extract meaningful message from object
            const msg = responseData.msg || responseData.error || responseData.title;
            errorMessage = msg ? String(msg) : `Server error: ${error.response.status}`;
          } else {
            errorMessage = `Server error: ${error.response.status}`;
          }
        } else {
          // Fallback: try to stringify the error
          errorMessage = String(error);
        }
      } catch (e) {
        console.error('Error extracting error message:', e);
        errorMessage = 'An unexpected error occurred. Please check the console for details.';
      }
      
      // Ensure we have a valid string message
      if (!errorMessage || errorMessage === '[object Object]') {
        errorMessage = 'Failed to clear cancelled appointments. Please check the console for details.';
      }
      
      setErrorSnackbar({
        open: true,
        message: errorMessage,
      });
    },
  });

  const handleClearCancelled = () => {
    setClearCancelledDialogOpen(true);
  };

  const handleClearCancelledConfirm = () => {
    try {
      clearCancelledMutation.mutate();
    } catch (error) {
      console.error('Error calling mutation:', error);
      setErrorSnackbar({
        open: true,
        message: 'An error occurred. Please try again.',
      });
    }
  };


  // Fetch all providers
  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: () => api.getProviders(),
    enabled: isAdmin,
  });

  // Fetch time slots
  const { data: timeSlotsData, isLoading: isLoadingSlots } = useQuery({
    queryKey: ['timeslots', selectedProviderId, selectedDate],
    queryFn: () => api.getTimeslots(selectedProviderId, selectedDate),
    enabled: selectedProviderId > 0 && selectedDate !== '',
  });

  // Filter appointments
  const filteredAppointments = appointments?.filter((appt: any) => {
    const matchesSearch = searchQuery === '' ||
      appt.provider_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      appt.user_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      appt.provider_department?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === '' || appt.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Mutations
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: any }) =>
      api.updateAppointment(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      setEditDialogOpen(false);
      setSelectedAppointment(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteAppointment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      setDeleteDialogOpen(false);
      setSelectedAppointment(null);
    },
  });

  const handleEdit = (appointment: any) => {
    setSelectedAppointment(appointment);
    setEditStatus(appointment.status);
    setEditNotes(appointment.notes || '');
    setEditProviderId(appointment.provider_id);
    const startDate = new Date(appointment.time_start);
    const endDate = new Date(appointment.time_end);
    setEditDate(startDate.toISOString().split('T')[0]);
    setEditTimeStart(startDate.toTimeString().slice(0, 5));
    setEditTimeEnd(endDate.toTimeString().slice(0, 5));
    setEditDialogOpen(true);
  };

  const handleViewTimeSlots = () => {
    if (editProviderId && editDate) {
      setSelectedProviderId(editProviderId);
      setSelectedDate(editDate);
      setTimeSlotsDialogOpen(true);
    }
  };

  const handleSelectTimeSlot = (slot: any) => {
    const start = new Date(slot.start);
    const end = new Date(slot.end);
    setEditTimeStart(start.toTimeString().slice(0, 5));
    setEditTimeEnd(end.toTimeString().slice(0, 5));
    setTimeSlotsDialogOpen(false);
  };

  const handleDelete = (appointment: any) => {
    setSelectedAppointment(appointment);
    setDeleteDialogOpen(true);
  };

  const handleUpdateSubmit = () => {
    if (!selectedAppointment) return;
    const timeStart = `${editDate}T${editTimeStart}:00`;
    const timeEnd = `${editDate}T${editTimeEnd}:00`;
    updateMutation.mutate({
      id: selectedAppointment.id,
      updates: { status: editStatus, notes: editNotes || null, time_start: timeStart, time_end: timeEnd },
    });
  };

  const handleDeleteConfirm = () => {
    if (!selectedAppointment) return;
    deleteMutation.mutate(selectedAppointment.id);
  };

  // Statistics
  const stats = {
    total: appointments?.length || 0,
    confirmed: appointments?.filter((a: any) => a.status === 'confirmed').length || 0,
    cancelled: appointments?.filter((a: any) => a.status === 'cancelled').length || 0,
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress sx={{ color: '#840132' }} />
      </Box>
    );
  }

  // Admin view
  if (isAdmin) {
    return (
      <Box sx={{ maxWidth: 1400, mx: 'auto' }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 800, background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', mb: 1 }}>
            Appointment Management
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>View and manage all patient appointments</Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {[
            { label: 'Total', value: stats.total, color: '#840132', icon: <EventIcon /> },
            { label: 'Confirmed', value: stats.confirmed, color: '#2e7d32', icon: <CheckIcon /> },
            { label: 'Cancelled', value: stats.cancelled, color: '#d32f2f', icon: <CancelIcon /> },
          ].map((stat) => (
            <Grid item xs={6} md={3} key={stat.label}>
              <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid', borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: alpha(stat.color, 0.1), color: stat.color }}>{stat.icon}</Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>{stat.value}</Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>{stat.label}</Typography>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Filters */}
        <Paper elevation={0} sx={{ p: 2, mb: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider', display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <TextField placeholder="Search appointments..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} size="small" sx={{ flexGrow: 1, minWidth: 250 }} InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: 'text.secondary' }} /></InputAdornment> }} />
          <TextField select size="small" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} sx={{ minWidth: 150 }} InputProps={{ startAdornment: <InputAdornment position="start"><FilterIcon sx={{ color: 'text.secondary', fontSize: 18 }} /></InputAdornment> }}>
            <MenuItem value="">All Status</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="confirmed">Confirmed</MenuItem>
            <MenuItem value="cancelled">Cancelled</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
          </TextField>
          <Button
            variant="outlined"
            color="error"
            size="small"
            onClick={handleClearCancelled}
            disabled={clearCancelledMutation.isPending || stats.cancelled === 0}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            {clearCancelledMutation.isPending ? 'Clearing...' : 'Clear Cancelled'}
          </Button>
        </Paper>

        {/* Table */}
        <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', overflow: 'hidden' }}>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: '#f8f9fa' }}>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>ID</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Patient</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Provider</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Date & Time</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Reason</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }} align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredAppointments && filteredAppointments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} sx={{ py: 8, textAlign: 'center' }}>
                    <EventIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'text.secondary' }}>No appointments found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredAppointments?.map((appt: any) => {
                  const status = statusConfig[appt.status] || statusConfig.confirmed;
                  return (
                    <TableRow key={appt.id} hover sx={{ '&:hover': { bgcolor: alpha('#840132', 0.02) } }}>
                      <TableCell><Chip label={`#${appt.id}`} size="small" variant="outlined" /></TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar sx={{ width: 36, height: 36, bgcolor: alpha('#840132', 0.1), color: '#840132', fontSize: '0.875rem' }}>{appt.user_name?.charAt(0)}</Avatar>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>{appt.user_name}</Typography>
                            <Typography variant="caption" sx={{ color: 'text.secondary' }}>{appt.user_email}</Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>{appt.provider_name}</Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>{appt.provider_department}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>{formatLebanonDate(appt.time_start)}</Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>{formatLebanonTimeOnly(appt.time_start)}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip icon={status.icon} label={status.label} size="small" sx={{ bgcolor: status.bgColor, color: status.color, fontWeight: 600, '& .MuiChip-icon': { color: status.color } }} />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ color: 'text.secondary', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>{appt.reason || '-'}</Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Edit"><IconButton size="small" onClick={() => handleEdit(appt)} sx={{ color: '#1976d2' }}><EditIcon fontSize="small" /></IconButton></Tooltip>
                        <Tooltip title="Cancel"><IconButton size="small" onClick={() => handleDelete(appt)} sx={{ color: '#d32f2f' }}><DeleteIcon fontSize="small" /></IconButton></Tooltip>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Edit Dialog */}
        <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
          <DialogTitle sx={{ pb: 1 }}><Typography variant="h5" sx={{ fontWeight: 700 }}>Edit Appointment</Typography></DialogTitle>
          <DialogContent>
            {selectedAppointment && (
              <>
                <Alert severity="info" sx={{ mt: 1, mb: 3, borderRadius: 2 }}>
                  <Typography variant="body2">Patient: <strong>{selectedAppointment.user_name}</strong> ({selectedAppointment.user_email})</Typography>
                </Alert>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField select fullWidth label="Provider / Doctor" value={editProviderId} onChange={(e) => setEditProviderId(Number(e.target.value))}>
                      {providers?.map((provider: any) => (<MenuItem key={provider.id} value={provider.id}>{provider.name} - {provider.department}</MenuItem>))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} md={4}><TextField fullWidth type="date" label="Date" value={editDate} onChange={(e) => setEditDate(e.target.value)} InputLabelProps={{ shrink: true }} /></Grid>
                  <Grid item xs={12} md={3}><TextField fullWidth type="time" label="Start Time" value={editTimeStart} onChange={(e) => setEditTimeStart(e.target.value)} InputLabelProps={{ shrink: true }} /></Grid>
                  <Grid item xs={12} md={3}><TextField fullWidth type="time" label="End Time" value={editTimeEnd} onChange={(e) => setEditTimeEnd(e.target.value)} InputLabelProps={{ shrink: true }} /></Grid>
                  <Grid item xs={12} md={2}><Button fullWidth variant="outlined" startIcon={<ScheduleIcon />} onClick={handleViewTimeSlots} disabled={!editProviderId || !editDate} sx={{ height: 56 }}>Slots</Button></Grid>
                  <Grid item xs={12}><TextField select fullWidth label="Status" value={editStatus} onChange={(e) => setEditStatus(e.target.value)}><MenuItem value="confirmed">Confirmed</MenuItem><MenuItem value="cancelled">Cancelled</MenuItem><MenuItem value="completed">Completed</MenuItem><MenuItem value="no_show">No Show</MenuItem></TextField></Grid>
                  <Grid item xs={12}><TextField fullWidth multiline rows={3} label="Admin Notes" value={editNotes} onChange={(e) => setEditNotes(e.target.value)} placeholder="Add notes..." /></Grid>
                </Grid>
              </>
            )}
          </DialogContent>
          <DialogActions sx={{ p: 3, pt: 2 }}>
            <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={handleUpdateSubmit} disabled={updateMutation.isPending} sx={{ bgcolor: '#840132', '&:hover': { bgcolor: '#6a0129' } }}>{updateMutation.isPending ? 'Updating...' : 'Update Appointment'}</Button>
          </DialogActions>
        </Dialog>

        {/* Time Slots Dialog */}
        <Dialog open={timeSlotsDialogOpen} onClose={() => setTimeSlotsDialogOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
          <DialogTitle><Typography variant="h6" sx={{ fontWeight: 700 }}>Available Time Slots</Typography><Typography variant="body2" color="text.secondary">{selectedDate && new Date(selectedDate).toLocaleDateString()} - {providers?.find((p: any) => p.id === selectedProviderId)?.name}</Typography></DialogTitle>
          <DialogContent>
            {isLoadingSlots ? (<Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress sx={{ color: '#840132' }} /></Box>) : timeSlotsData?.slots && timeSlotsData.slots.length > 0 ? (
              <List>{timeSlotsData.slots.map((slot: any) => (<ListItem key={slot.slot_id} disablePadding sx={{ mb: 1 }}><ListItemButton onClick={() => handleSelectTimeSlot(slot)} disabled={!slot.available} sx={{ borderRadius: 2, border: '1px solid', borderColor: slot.available ? 'divider' : 'transparent', bgcolor: slot.available ? 'transparent' : '#f5f5f5' }}><ListItemText primary={`${formatLebanonTimeOnly(slot.start)} - ${formatLebanonTimeOnly(slot.end)}`} secondary={slot.available ? 'Available' : 'Booked'} primaryTypographyProps={{ fontWeight: 600, color: slot.available ? 'text.primary' : 'text.disabled' }} />{slot.available && <Chip label="Select" color="primary" size="small" sx={{ bgcolor: '#840132' }} />}</ListItemButton></ListItem>))}</List>
            ) : (<Alert severity="warning" sx={{ borderRadius: 2 }}>No time slots available for this date.</Alert>)}
          </DialogContent>
          <DialogActions sx={{ p: 2 }}><Button onClick={() => setTimeSlotsDialogOpen(false)}>Close</Button></DialogActions>
        </Dialog>

        {/* Delete Dialog */}
        <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} PaperProps={{ sx: { borderRadius: 3 } }}>
          <DialogTitle sx={{ pb: 1 }}><Typography variant="h6" sx={{ fontWeight: 700, color: '#d32f2f' }}>Cancel Appointment</Typography></DialogTitle>
          <DialogContent>{selectedAppointment && (<Typography>Are you sure you want to cancel the appointment for <strong>{selectedAppointment.user_name}</strong> with <strong>{selectedAppointment.provider_name}</strong> on {formatLebanonTime(selectedAppointment.time_start)}?</Typography>)}</DialogContent>
          <DialogActions sx={{ p: 2 }}><Button onClick={() => setDeleteDialogOpen(false)}>No, Keep It</Button><Button variant="contained" color="error" onClick={handleDeleteConfirm} disabled={deleteMutation.isPending}>{deleteMutation.isPending ? 'Cancelling...' : 'Yes, Cancel'}</Button></DialogActions>
        </Dialog>

        {/* Clear Cancelled Confirmation Dialog */}
        <Dialog open={clearCancelledDialogOpen} onClose={() => setClearCancelledDialogOpen(false)} PaperProps={{ sx: { borderRadius: 3 } }}>
          <DialogTitle sx={{ pb: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#d32f2f' }}>Clear Cancelled Appointments</Typography>
          </DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to permanently remove all cancelled appointments from the system? 
              This action cannot be undone.
            </Typography>
            <Alert severity="warning" sx={{ mt: 2, borderRadius: 2 }}>
              This will delete all cancelled appointments from the database.
            </Alert>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setClearCancelledDialogOpen(false)}>Cancel</Button>
            <Button 
              variant="contained" 
              color="error" 
              onClick={handleClearCancelledConfirm} 
              disabled={clearCancelledMutation.isPending}
            >
              {clearCancelledMutation.isPending ? 'Clearing...' : 'Yes, Clear All'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Error Snackbar */}
        <Snackbar
          open={errorSnackbar.open}
          autoHideDuration={6000}
          onClose={() => setErrorSnackbar({ open: false, message: '' })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="error" onClose={() => setErrorSnackbar({ open: false, message: '' })}>
            {errorSnackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    );
  }

  // Patient view
  const cancelledCount = appointments?.filter((a: any) => a.status === 'cancelled').length || 0;
  
  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', mb: 1 }}>My Appointments</Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>View and manage your upcoming healthcare appointments</Typography>
        </Box>
        {cancelledCount > 0 && (
          <Button
            variant="outlined"
            color="error"
            size="small"
            onClick={handleClearCancelled}
            disabled={clearCancelledMutation.isPending}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            {clearCancelledMutation.isPending ? 'Clearing...' : 'Clear Cancelled'}
          </Button>
        )}
      </Box>
      {(!appointments || appointments.length === 0) ? (
        <Paper elevation={0} sx={{ p: 6, borderRadius: 4, border: '1px solid', borderColor: 'divider', textAlign: 'center' }}>
          <EventIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 1 }}>No appointments yet</Typography>
          <Typography variant="body2" sx={{ color: 'text.disabled' }}>Use our AI Assistant to book your first appointment</Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>{appointments.map((appt: any, index: number) => (<Grid item xs={12} md={6} key={appt.id}><AppointmentCard appointment={appt} index={index} /></Grid>))}</Grid>
      )}

      {/* Clear Cancelled Confirmation Dialog */}
      <Dialog open={clearCancelledDialogOpen} onClose={() => setClearCancelledDialogOpen(false)} PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#d32f2f' }}>Clear Cancelled Appointments</Typography>
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to permanently remove all cancelled appointments from your view? 
            This action cannot be undone.
          </Typography>
          {isAdmin && (
            <Alert severity="info" sx={{ mt: 2, borderRadius: 2 }}>
              This will remove all cancelled appointments from the system.
            </Alert>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setClearCancelledDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            color="error" 
            onClick={handleClearCancelledConfirm} 
            disabled={clearCancelledMutation.isPending}
          >
            {clearCancelledMutation.isPending ? 'Clearing...' : 'Yes, Clear All'}
          </Button>
          </DialogActions>
        </Dialog>

        {/* Error Snackbar */}
        <Snackbar
          open={errorSnackbar.open}
          autoHideDuration={6000}
          onClose={() => setErrorSnackbar({ open: false, message: '' })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="error" onClose={() => setErrorSnackbar({ open: false, message: '' })}>
            {errorSnackbar.message}
          </Alert>
        </Snackbar>
    </Box>
  );
}
