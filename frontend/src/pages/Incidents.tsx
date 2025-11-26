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
  Avatar,
  alpha,
  Fade,
  Divider,
  InputAdornment,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  AccessTime as AccessTimeIcon,
  PriorityHigh as UrgentIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Schedule as ScheduleIcon,
  SupportAgent as SupportIcon,
  Close as CloseIcon,
  Edit as EditIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';

// Stats Card Component
function StatCard({ 
  icon, 
  label, 
  value, 
  color, 
  onClick,
  active 
}: { 
  icon: React.ReactNode; 
  label: string; 
  value: number | string; 
  color: string;
  onClick?: () => void;
  active?: boolean;
}) {
  return (
    <Card
      elevation={0}
      onClick={onClick}
      sx={{
        borderRadius: 3,
        border: '1px solid',
        borderColor: active ? color : 'divider',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        bgcolor: active ? alpha(color, 0.05) : 'background.paper',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
          boxShadow: `0 8px 24px ${alpha(color, 0.15)}`,
          borderColor: color,
        } : {},
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar
            sx={{
              width: 52,
              height: 52,
              bgcolor: alpha(color, 0.12),
              color: color,
            }}
          >
            {icon}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, mb: 0.5 }}>
              {label}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700, color: color, lineHeight: 1 }}>
              {value}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

// Status Tab Button
function StatusTab({ 
  label, 
  count, 
  active, 
  color, 
  onClick 
}: { 
  label: string; 
  count: number; 
  active: boolean; 
  color: string; 
  onClick: () => void;
}) {
  return (
    <Button
      onClick={onClick}
      variant={active ? 'contained' : 'text'}
      sx={{
        px: 3,
        py: 1.5,
        borderRadius: 2,
        textTransform: 'none',
        fontWeight: 600,
        bgcolor: active ? color : 'transparent',
        color: active ? 'white' : 'text.secondary',
        '&:hover': {
          bgcolor: active ? color : alpha(color, 0.08),
        },
      }}
    >
      {label}
      <Chip
        label={count}
        size="small"
        sx={{
          ml: 1,
          height: 22,
          minWidth: 28,
          bgcolor: active ? 'rgba(255,255,255,0.2)' : alpha(color, 0.12),
          color: active ? 'white' : color,
          fontWeight: 700,
          fontSize: '0.75rem',
        }}
      />
    </Button>
  );
}

export default function IncidentsPage() {
  const [tabValue, setTabValue] = useState(0);
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);
  const [updateStatus, setUpdateStatus] = useState('');
  const [updatePriority, setUpdatePriority] = useState('');
  const [adminNotes, setAdminNotes] = useState('');
  const [resolution, setResolution] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

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

  // Filter incidents by search
  const filteredIncidents = incidents.filter((incident: any) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      incident.patient_name?.toLowerCase().includes(query) ||
      incident.patient_email?.toLowerCase().includes(query) ||
      incident.subject?.toLowerCase().includes(query) ||
      `#${incident.id}`.includes(query)
    );
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

  const handleQuickResolve = async (incident: any, e: React.MouseEvent) => {
    e.stopPropagation();
    updateMutation.mutate({
      id: incident.id,
      updates: { status: 'resolved' },
    });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#d32f2f';
      case 'high': return '#ed6c02';
      case 'medium': return '#0288d1';
      default: return '#757575';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return '#2e7d32';
      case 'in_progress': return '#1976d2';
      case 'pending': return '#ed6c02';
      default: return '#757575';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent': return <UrgentIcon sx={{ fontSize: 16 }} />;
      case 'high': return <WarningIcon sx={{ fontSize: 16 }} />;
      default: return null;
    }
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <Box sx={{ pb: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <Avatar
            sx={{
              width: 48,
              height: 48,
              bgcolor: alpha('#840132', 0.1),
              color: '#840132',
            }}
          >
            <SupportIcon />
          </Avatar>
          <Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 800,
                background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Incident Management
            </Typography>
            <Typography variant="body1" sx={{ color: 'text.secondary' }}>
              Monitor and resolve patient handover requests
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              icon={<SupportIcon />}
              label="Total Incidents"
              value={stats.total_incidents}
              color="#840132"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              icon={<AccessTimeIcon />}
              label="Pending"
              value={stats.pending_count}
              color="#ed6c02"
              onClick={() => setTabValue(1)}
              active={tabValue === 1}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              icon={<ScheduleIcon />}
              label="In Progress"
              value={stats.in_progress_count}
              color="#1976d2"
              onClick={() => setTabValue(2)}
              active={tabValue === 2}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              icon={<UrgentIcon />}
              label="High Priority"
              value={stats.high_priority_count + stats.urgent_count}
              color="#d32f2f"
            />
          </Grid>
        </Grid>
      )}

      {/* Filter Bar */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 3,
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        {/* Status Tabs */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <StatusTab label="All" count={stats?.total_incidents || 0} active={tabValue === 0} color="#840132" onClick={() => setTabValue(0)} />
          <StatusTab label="Pending" count={stats?.pending_count || 0} active={tabValue === 1} color="#ed6c02" onClick={() => setTabValue(1)} />
          <StatusTab label="In Progress" count={stats?.in_progress_count || 0} active={tabValue === 2} color="#1976d2" onClick={() => setTabValue(2)} />
          <StatusTab label="Resolved" count={stats?.resolved_count || 0} active={tabValue === 3} color="#2e7d32" onClick={() => setTabValue(3)} />
        </Box>

        {/* Search */}
        <TextField
          size="small"
          placeholder="Search incidents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{
            minWidth: 280,
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              bgcolor: 'background.default',
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {/* Incidents Table */}
      <Paper
        elevation={0}
        sx={{
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          overflow: 'hidden',
        }}
      >
        {isLoading && <LinearProgress sx={{ bgcolor: alpha('#840132', 0.1), '& .MuiLinearProgress-bar': { bgcolor: '#840132' } }} />}
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: alpha('#840132', 0.03) }}>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary', py: 2 }}>Incident</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary', py: 2 }}>Patient</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary', py: 2 }}>Subject</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary', py: 2 }}>Priority</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary', py: 2 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary', py: 2 }}>Time</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary', py: 2 }} align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {!isLoading && filteredIncidents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7}>
                    <Box sx={{ py: 8, textAlign: 'center' }}>
                      <Avatar sx={{ width: 64, height: 64, bgcolor: alpha('#840132', 0.1), color: '#840132', mx: 'auto', mb: 2 }}>
                        <CheckCircleIcon sx={{ fontSize: 32 }} />
                      </Avatar>
                      <Typography variant="h6" sx={{ color: 'text.secondary', mb: 1 }}>
                        No incidents found
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.disabled' }}>
                        {searchQuery ? 'Try adjusting your search' : 'All clear! No patient escalations at this time.'}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredIncidents.map((incident: any, index: number) => (
                  <Fade in key={incident.id} timeout={200 + index * 50}>
                    <TableRow
                      hover
                      onClick={() => handleViewDetails(incident)}
                      sx={{
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          bgcolor: alpha('#840132', 0.02),
                        },
                      }}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar
                            sx={{
                              width: 36,
                              height: 36,
                              bgcolor: alpha(getStatusColor(incident.status), 0.1),
                              color: getStatusColor(incident.status),
                              fontSize: '0.8rem',
                              fontWeight: 700,
                            }}
                          >
                            #{incident.id}
                          </Avatar>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                            {incident.patient_name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                            {incident.patient_email}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            maxWidth: 250,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {incident.subject}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getPriorityIcon(incident.priority) || undefined}
                          label={incident.priority.toUpperCase()}
                          size="small"
                          sx={{
                            bgcolor: alpha(getPriorityColor(incident.priority), 0.1),
                            color: getPriorityColor(incident.priority),
                            fontWeight: 700,
                            fontSize: '0.7rem',
                            borderRadius: 1.5,
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={incident.status.replace('_', ' ').toUpperCase()}
                          size="small"
                          sx={{
                            bgcolor: alpha(getStatusColor(incident.status), 0.1),
                            color: getStatusColor(incident.status),
                            fontWeight: 700,
                            fontSize: '0.7rem',
                            borderRadius: 1.5,
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                          <HistoryIcon sx={{ fontSize: 16 }} />
                          <Typography variant="caption">
                            {getTimeAgo(incident.created_at)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={(e) => { e.stopPropagation(); handleViewDetails(incident); }}
                              sx={{
                                bgcolor: alpha('#840132', 0.08),
                                color: '#840132',
                                '&:hover': { bgcolor: alpha('#840132', 0.15) },
                              }}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          {incident.status !== 'resolved' && (
                            <Tooltip title="Quick Resolve">
                              <IconButton
                                size="small"
                                onClick={(e) => handleQuickResolve(incident, e)}
                                sx={{
                                  bgcolor: alpha('#2e7d32', 0.08),
                                  color: '#2e7d32',
                                  '&:hover': { bgcolor: alpha('#2e7d32', 0.15) },
                                }}
                              >
                                <CheckCircleIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  </Fade>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            overflow: 'hidden',
          },
        }}
      >
        {selectedIncident && (
          <>
            {/* Dialog Header */}
            <Box
              sx={{
                background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)',
                color: 'white',
                p: 3,
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="overline" sx={{ opacity: 0.8 }}>
                    Incident #{selectedIncident.id}
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 700, mt: 0.5 }}>
                    {selectedIncident.subject}
                  </Typography>
                </Box>
                <IconButton
                  onClick={() => setDetailsDialogOpen(false)}
                  sx={{ color: 'white', opacity: 0.8, '&:hover': { opacity: 1 } }}
                >
                  <CloseIcon />
                </IconButton>
              </Box>
              <Box sx={{ display: 'flex', gap: 1.5, mt: 2 }}>
                <Chip
                  label={selectedIncident.priority.toUpperCase()}
                  size="small"
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    fontWeight: 700,
                  }}
                />
                <Chip
                  label={selectedIncident.status.replace('_', ' ').toUpperCase()}
                  size="small"
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    fontWeight: 700,
                  }}
                />
              </Box>
            </Box>

            <DialogContent sx={{ p: 3 }}>
              <Grid container spacing={3}>
                {/* Patient Info Card */}
                <Grid item xs={12} md={6}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2.5,
                      borderRadius: 2,
                      bgcolor: alpha('#840132', 0.03),
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: '#840132' }}>
                      Patient Information
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Avatar sx={{ bgcolor: alpha('#840132', 0.1), color: '#840132' }}>
                        <PersonIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                          {selectedIncident.patient_name}
                        </Typography>
                      </Box>
                    </Box>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <EmailIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                        <Typography variant="body2">{selectedIncident.patient_email}</Typography>
                      </Box>
                      {selectedIncident.patient_phone && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <PhoneIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                          <Typography variant="body2">{selectedIncident.patient_phone}</Typography>
                        </Box>
                      )}
                    </Box>
                  </Paper>
                </Grid>

                {/* Timestamps Card */}
                <Grid item xs={12} md={6}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2.5,
                      borderRadius: 2,
                      bgcolor: alpha('#1976d2', 0.03),
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: '#1976d2' }}>
                      Timeline
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: alpha('#1976d2', 0.1), color: '#1976d2' }}>
                          <AccessTimeIcon sx={{ fontSize: 16 }} />
                        </Avatar>
                        <Box>
                          <Typography variant="caption" sx={{ color: 'text.secondary' }}>Created</Typography>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {new Date(selectedIncident.created_at).toLocaleString()}
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: alpha('#ed6c02', 0.1), color: '#ed6c02' }}>
                          <EditIcon sx={{ fontSize: 16 }} />
                        </Avatar>
                        <Box>
                          <Typography variant="caption" sx={{ color: 'text.secondary' }}>Last Updated</Typography>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {new Date(selectedIncident.updated_at).toLocaleString()}
                          </Typography>
                        </Box>
                      </Box>
                      {selectedIncident.resolved_at && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar sx={{ width: 32, height: 32, bgcolor: alpha('#2e7d32', 0.1), color: '#2e7d32' }}>
                            <CheckCircleIcon sx={{ fontSize: 16 }} />
                          </Avatar>
                          <Box>
                            <Typography variant="caption" sx={{ color: 'text.secondary' }}>Resolved</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {new Date(selectedIncident.resolved_at).toLocaleString()}
                            </Typography>
                          </Box>
                        </Box>
                      )}
                    </Box>
                  </Paper>
                </Grid>

                {/* Conversation Summary */}
                <Grid item xs={12}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: 'text.primary' }}>
                    Conversation Summary
                  </Typography>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      borderRadius: 2,
                      bgcolor: 'grey.50',
                      border: '1px solid',
                      borderColor: 'divider',
                      maxHeight: 250,
                      overflow: 'auto',
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.7,
                        color: 'text.secondary',
                      }}
                    >
                      {selectedIncident.chat_summary}
                    </Typography>
                  </Paper>
                </Grid>

                {/* Admin Notes */}
                {selectedIncident.admin_notes && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: 'text.primary' }}>
                      Admin Notes
                    </Typography>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2.5,
                        borderRadius: 2,
                        bgcolor: alpha('#ed6c02', 0.05),
                        border: '1px solid',
                        borderColor: alpha('#ed6c02', 0.2),
                      }}
                    >
                      <Typography variant="body2">{selectedIncident.admin_notes}</Typography>
                    </Paper>
                  </Grid>
                )}

                {/* Resolution */}
                {selectedIncident.resolution && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: 'text.primary' }}>
                      Resolution
                    </Typography>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2.5,
                        borderRadius: 2,
                        bgcolor: alpha('#2e7d32', 0.05),
                        border: '1px solid',
                        borderColor: alpha('#2e7d32', 0.2),
                      }}
                    >
                      <Typography variant="body2">{selectedIncident.resolution}</Typography>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </DialogContent>

            <DialogActions sx={{ p: 3, pt: 0 }}>
              <Button
                onClick={() => setDetailsDialogOpen(false)}
                sx={{ color: 'text.secondary' }}
              >
                Close
              </Button>
              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={handleOpenUpdate}
                sx={{
                  bgcolor: '#840132',
                  '&:hover': { bgcolor: '#5e0124' },
                  borderRadius: 2,
                  px: 3,
                }}
              >
                Update Incident
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Update Dialog */}
      <Dialog
        open={updateDialogOpen}
        onClose={() => setUpdateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Update Incident
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Modify status, priority, and add notes
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={6}>
              <TextField
                select
                fullWidth
                label="Status"
                value={updateStatus}
                onChange={(e) => setUpdateStatus(e.target.value)}
                size="small"
              >
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="resolved">Resolved</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField
                select
                fullWidth
                label="Priority"
                value={updatePriority}
                onChange={(e) => setUpdatePriority(e.target.value)}
                size="small"
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Admin Notes"
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder="Internal notes about this incident..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Resolution"
                value={resolution}
                onChange={(e) => setResolution(e.target.value)}
                placeholder="Describe how the issue was resolved..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button onClick={() => setUpdateDialogOpen(false)} sx={{ color: 'text.secondary' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleUpdateSubmit}
            disabled={updateMutation.isPending}
            startIcon={<CheckCircleIcon />}
            sx={{
              bgcolor: '#840132',
              '&:hover': { bgcolor: '#5e0124' },
              borderRadius: 2,
              px: 3,
            }}
          >
            {updateMutation.isPending ? 'Updating...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
