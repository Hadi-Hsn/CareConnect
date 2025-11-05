import React, { useState } from 'react';
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
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

export default function AppointmentsPage() {
  const currentUser = api.getCurrentUser();
  const isAdmin = currentUser?.role === 'admin' || currentUser?.role === 'staff';
  
  const [selectedAppointment, setSelectedAppointment] = useState<any>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [timeSlotsDialogOpen, setTimeSlotsDialogOpen] = useState(false);
  
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

  // Fetch appointments - all for admin, user's own for patients
  const { data: appointments, isLoading } = useQuery({
    queryKey: ['appointments', isAdmin],
    queryFn: () => isAdmin ? api.getAppointments() : api.getAppointments({ user_id: currentUser?.id }),
  });

  // Fetch all providers
  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: () => api.getProviders(),
    enabled: isAdmin,
  });

  // Fetch time slots when provider and date are selected
  const { data: timeSlotsData, isLoading: isLoadingSlots } = useQuery({
    queryKey: ['timeslots', selectedProviderId, selectedDate],
    queryFn: () => api.getTimeslots(selectedProviderId, selectedDate),
    enabled: selectedProviderId > 0 && selectedDate !== '',
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: any }) =>
      api.updateAppointment(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      setEditDialogOpen(false);
      setSelectedAppointment(null);
    },
  });

  // Delete mutation
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
    
    // Parse the datetime for date and time inputs
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
    
    // Combine date and time for the update
    const timeStart = `${editDate}T${editTimeStart}:00`;
    const timeEnd = `${editDate}T${editTimeEnd}:00`;
    
    updateMutation.mutate({
      id: selectedAppointment.id,
      updates: {
        status: editStatus,
        notes: editNotes || null,
        time_start: timeStart,
        time_end: timeEnd,
      },
    });
  };

  const handleDeleteConfirm = () => {
    if (!selectedAppointment) return;
    deleteMutation.mutate(selectedAppointment.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'cancelled':
        return 'error';
      case 'completed':
        return 'info';
      case 'no_show':
        return 'default';
      default:
        return 'default';
    }
  };

  if (isLoading) return <CircularProgress />;

  // Admin view - Table format
  if (isAdmin) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          All Appointments
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Manage all patient appointments across the system
        </Typography>

        <TableContainer component={Paper} sx={{ mt: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Patient</TableCell>
                <TableCell>Provider</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Date & Time</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {appointments && appointments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No appointments found
                  </TableCell>
                </TableRow>
              ) : (
                appointments?.map((appt: any) => (
                  <TableRow key={appt.id} hover>
                    <TableCell>#{appt.id}</TableCell>
                    <TableCell>
                      <Typography variant="body2">{appt.user_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {appt.user_email}
                      </Typography>
                    </TableCell>
                    <TableCell>{appt.provider_name}</TableCell>
                    <TableCell>{appt.provider_department}</TableCell>
                    <TableCell>
                      {new Date(appt.time_start).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={appt.status.toUpperCase()}
                        size="small"
                        color={getStatusColor(appt.status) as any}
                      />
                    </TableCell>
                    <TableCell>{appt.reason || '-'}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(appt)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(appt)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Edit Dialog */}
        <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Edit Appointment</DialogTitle>
          <DialogContent>
            {selectedAppointment && (
              <>
                <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
                  Patient: <strong>{selectedAppointment.user_name}</strong> ({selectedAppointment.user_email})
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      select
                      fullWidth
                      label="Provider / Doctor"
                      value={editProviderId}
                      onChange={(e) => setEditProviderId(Number(e.target.value))}
                      margin="normal"
                    >
                      {providers?.map((provider: any) => (
                        <MenuItem key={provider.id} value={provider.id}>
                          {provider.name} - {provider.department} ({provider.type})
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      type="date"
                      label="Date"
                      value={editDate}
                      onChange={(e) => setEditDate(e.target.value)}
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12} md={3}>
                    <TextField
                      fullWidth
                      type="time"
                      label="Start Time"
                      value={editTimeStart}
                      onChange={(e) => setEditTimeStart(e.target.value)}
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12} md={3}>
                    <TextField
                      fullWidth
                      type="time"
                      label="End Time"
                      value={editTimeEnd}
                      onChange={(e) => setEditTimeEnd(e.target.value)}
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12} md={2}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<ScheduleIcon />}
                      onClick={handleViewTimeSlots}
                      disabled={!editProviderId || !editDate}
                      sx={{ mt: 2, height: 56 }}
                    >
                      Slots
                    </Button>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      select
                      fullWidth
                      label="Status"
                      value={editStatus}
                      onChange={(e) => setEditStatus(e.target.value)}
                      margin="normal"
                    >
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="confirmed">Confirmed</MenuItem>
                      <MenuItem value="cancelled">Cancelled</MenuItem>
                      <MenuItem value="completed">Completed</MenuItem>
                      <MenuItem value="no_show">No Show</MenuItem>
                    </TextField>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Admin Notes"
                      value={editNotes}
                      onChange={(e) => setEditNotes(e.target.value)}
                      margin="normal"
                      placeholder="Add notes about this appointment..."
                    />
                  </Grid>
                </Grid>
              </>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleUpdateSubmit}
              disabled={updateMutation.isPending}
            >
              {updateMutation.isPending ? 'Updating...' : 'Update Appointment'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Time Slots Dialog */}
        <Dialog
          open={timeSlotsDialogOpen}
          onClose={() => setTimeSlotsDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            Available Time Slots
            <Typography variant="body2" color="text.secondary">
              {selectedDate && new Date(selectedDate).toLocaleDateString()} -{' '}
              {providers?.find((p: any) => p.id === selectedProviderId)?.name}
            </Typography>
          </DialogTitle>
          <DialogContent>
            {isLoadingSlots ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : timeSlotsData?.slots && timeSlotsData.slots.length > 0 ? (
              <List>
                {timeSlotsData.slots.map((slot: any) => (
                  <ListItem key={slot.slot_id} disablePadding>
                    <ListItemButton
                      onClick={() => handleSelectTimeSlot(slot)}
                      disabled={!slot.available}
                    >
                      <ListItemText
                        primary={`${new Date(slot.start).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })} - ${new Date(slot.end).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}`}
                        secondary={slot.available ? 'Available' : 'Booked'}
                        primaryTypographyProps={{
                          color: slot.available ? 'text.primary' : 'text.disabled',
                        }}
                      />
                      {slot.available && (
                        <Chip label="Select" color="primary" size="small" />
                      )}
                    </ListItemButton>
                    <Divider />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Alert severity="warning">
                No time slots available for this date. Try a different date.
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setTimeSlotsDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* Delete Dialog */}
        <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
          <DialogTitle>Cancel Appointment</DialogTitle>
          <DialogContent>
            {selectedAppointment && (
              <Typography>
                Are you sure you want to cancel the appointment for{' '}
                <strong>{selectedAppointment.user_name}</strong> with{' '}
                <strong>{selectedAppointment.provider_name}</strong> on{' '}
                {new Date(selectedAppointment.time_start).toLocaleString()}?
              </Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>No, Keep It</Button>
            <Button
              variant="contained"
              color="error"
              onClick={handleDeleteConfirm}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Cancelling...' : 'Yes, Cancel'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }

  // Patient view - Card format
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        My Appointments
      </Typography>
      <Grid container spacing={3}>
        {appointments?.map((appt) => (
          <Grid item xs={12} md={6} key={appt.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">{appt.provider_name}</Typography>
                  <Chip label={appt.status} color={getStatusColor(appt.status) as any} size="small" />
                </Box>
                <Typography color="text.secondary">{appt.provider_department}</Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {new Date(appt.time_start).toLocaleString()}
                </Typography>
                {appt.reason && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Reason: {appt.reason}
                  </Typography>
                )}
                {appt.confirmation_code && (
                  <Chip label={`Code: ${appt.confirmation_code}`} size="small" sx={{ mt: 1 }} />
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
