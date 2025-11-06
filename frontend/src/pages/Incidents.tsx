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
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

export default function IncidentsPage() {
  const [tabValue, setTabValue] = useState(0);
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);
  const [updateStatus, setUpdateStatus] = useState('');
  const [updatePriority, setUpdatePriority] = useState('');
  const [adminNotes, setAdminNotes] = useState('');
  const [resolution, setResolution] = useState('');

  const queryClient = useQueryClient();

  // Filter based on tab
  const statusFilter = tabValue === 0 ? undefined : 
    tabValue === 1 ? 'pending' :
    tabValue === 2 ? 'in_progress' : 
    'resolved';

  // Fetch incidents
  const { data: incidents = [], isLoading } = useQuery({
    queryKey: ['incidents', statusFilter],
    queryFn: () => api.getIncidents(statusFilter),
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['incident-stats'],
    queryFn: () => api.getIncidentStats(),
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: any }) =>
      api.updateIncident(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['incident-stats'] });
      setUpdateDialogOpen(false);
      setDetailsDialogOpen(false);
    },
  });

  const handleViewDetails = async (incident: any) => {
    const details = await api.getIncident(incident.id);
    setSelectedIncident(details);
    setDetailsDialogOpen(true);
  };

  const handleOpenUpdate = () => {
    if (selectedIncident) {
      setUpdateStatus(selectedIncident.status);
      setUpdatePriority(selectedIncident.priority);
      setAdminNotes(selectedIncident.admin_notes || '');
      setResolution(selectedIncident.resolution || '');
      setUpdateDialogOpen(true);
    }
  };

  const handleUpdateSubmit = () => {
    if (!selectedIncident) return;

    updateMutation.mutate({
      id: selectedIncident.id,
      updates: {
        status: updateStatus,
        priority: updatePriority,
        admin_notes: adminNotes || null,
        resolution: resolution || null,
      },
    });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Patient Handover Incidents
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Manage patient requests for human assistance
      </Typography>

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3, mt: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Incidents
                </Typography>
                <Typography variant="h4">{stats.total_incidents}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Pending
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {stats.pending_count}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  In Progress
                </Typography>
                <Typography variant="h4" color="primary.main">
                  {stats.in_progress_count}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  High/Urgent
                </Typography>
                <Typography variant="h4" color="error.main">
                  {stats.high_priority_count + stats.urgent_count}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="All" />
          <Tab label="Pending" />
          <Tab label="In Progress" />
          <Tab label="Resolved" />
        </Tabs>
      </Paper>

      {/* Incidents Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Subject</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : incidents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No incidents found
                </TableCell>
              </TableRow>
            ) : (
              incidents.map((incident: any) => (
                <TableRow key={incident.id} hover>
                  <TableCell>#{incident.id}</TableCell>
                  <TableCell>
                    <Typography variant="body2">{incident.patient_name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {incident.patient_email}
                    </Typography>
                  </TableCell>
                  <TableCell>{incident.subject}</TableCell>
                  <TableCell>
                    <Chip
                      label={incident.priority.toUpperCase()}
                      size="small"
                      color={getPriorityColor(incident.priority) as any}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={incident.status.replace('_', ' ').toUpperCase()}
                      size="small"
                      color={getStatusColor(incident.status) as any}
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(incident.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleViewDetails(incident)}
                      color="primary"
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedIncident && (
          <>
            <DialogTitle>
              Incident #{selectedIncident.id} - {selectedIncident.subject}
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Alert severity={getPriorityColor(selectedIncident.priority) as any}>
                    Priority: {selectedIncident.priority.toUpperCase()} | Status:{' '}
                    {selectedIncident.status.replace('_', ' ').toUpperCase()}
                  </Alert>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Patient Information
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="body2" fontWeight="bold">
                      {selectedIncident.patient_name}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <EmailIcon fontSize="small" />
                    <Typography variant="body2">{selectedIncident.patient_email}</Typography>
                  </Box>
                  {selectedIncident.patient_phone && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <PhoneIcon fontSize="small" />
                      <Typography variant="body2">{selectedIncident.patient_phone}</Typography>
                    </Box>
                  )}
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Timestamps
                  </Typography>
                  <Typography variant="body2">
                    Created: {new Date(selectedIncident.created_at).toLocaleString()}
                  </Typography>
                  <Typography variant="body2">
                    Updated: {new Date(selectedIncident.updated_at).toLocaleString()}
                  </Typography>
                  {selectedIncident.resolved_at && (
                    <Typography variant="body2">
                      Resolved: {new Date(selectedIncident.resolved_at).toLocaleString()}
                    </Typography>
                  )}
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Conversation Summary
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{ p: 2, maxHeight: 300, overflow: 'auto', whiteSpace: 'pre-wrap' }}
                  >
                    {selectedIncident.chat_summary}
                  </Paper>
                </Grid>

                {selectedIncident.admin_notes && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Admin Notes
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2">{selectedIncident.admin_notes}</Typography>
                    </Paper>
                  </Grid>
                )}

                {selectedIncident.resolution && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Resolution
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2">{selectedIncident.resolution}</Typography>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
              <Button variant="contained" startIcon={<AssignmentIcon />} onClick={handleOpenUpdate}>
                Update Incident
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Update Dialog */}
      <Dialog open={updateDialogOpen} onClose={() => setUpdateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Update Incident</DialogTitle>
        <DialogContent>
          <TextField
            select
            fullWidth
            label="Status"
            value={updateStatus}
            onChange={(e) => setUpdateStatus(e.target.value)}
            margin="normal"
          >
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="in_progress">In Progress</MenuItem>
            <MenuItem value="resolved">Resolved</MenuItem>
            <MenuItem value="closed">Closed</MenuItem>
          </TextField>

          <TextField
            select
            fullWidth
            label="Priority"
            value={updatePriority}
            onChange={(e) => setUpdatePriority(e.target.value)}
            margin="normal"
          >
            <MenuItem value="low">Low</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="urgent">Urgent</MenuItem>
          </TextField>

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Admin Notes"
            value={adminNotes}
            onChange={(e) => setAdminNotes(e.target.value)}
            margin="normal"
          />

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Resolution"
            value={resolution}
            onChange={(e) => setResolution(e.target.value)}
            margin="normal"
            placeholder="Describe how the issue was resolved..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpdateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleUpdateSubmit}
            disabled={updateMutation.isPending}
            startIcon={<CheckCircleIcon />}
          >
            {updateMutation.isPending ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
