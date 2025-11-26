/**
 * Providers Management Page
 * Professional admin interface for managing healthcare providers and documents
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  InputAdornment,
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
  Avatar,
  Tabs,
  Tab,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tooltip,
  Switch,
  FormControlLabel,
  Divider,
  alpha,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Download as DownloadIcon,
  LocalHospital as HospitalIcon,
  Description as DocumentIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  MedicalServices as MedicalIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';
import { DEPARTMENTS } from '@/lib/constants';

const BRAND_COLOR = '#840132';

export default function ProvidersPage() {
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selectedProvider, setSelectedProvider] = useState<any>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [generalDocFile, setGeneralDocFile] = useState<File | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    department: '',
    specialty: '',
    bio: '',
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [availability, setAvailability] = useState<{
    [key: string]: { enabled: boolean; start: string; end: string };
  }>({
    monday: { enabled: false, start: '09:00', end: '17:00' },
    tuesday: { enabled: false, start: '09:00', end: '17:00' },
    wednesday: { enabled: false, start: '09:00', end: '17:00' },
    thursday: { enabled: false, start: '09:00', end: '17:00' },
    friday: { enabled: false, start: '09:00', end: '17:00' },
    saturday: { enabled: false, start: '09:00', end: '17:00' },
    sunday: { enabled: false, start: '09:00', end: '17:00' },
  });

  const queryClient = useQueryClient();

  const { data: providers, isLoading } = useQuery({
    queryKey: ['providers', departmentFilter, typeFilter],
    queryFn: () => {
      const filters: any = {};
      if (departmentFilter) filters.department = departmentFilter;
      if (typeFilter) filters.provider_type = typeFilter;
      return api.getProviders(filters);
    },
  });

  // Fetch hospital documents
  const { data: documents, isLoading: documentsLoading } = useQuery({
    queryKey: ['hospital-documents'],
    queryFn: () => api.listDocuments(),
    enabled: tabValue === 1,
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => api.createProvider(data),
    onSuccess: async (createdProvider: any) => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      if (selectedFile) {
        try {
          await api.uploadPDF(selectedFile, 'provider', createdProvider.id);
        } catch (err) {
          console.error('provider document upload failed', err);
        }
      }
      setCreateDialogOpen(false);
      resetForm();
      setSelectedFile(null);
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => api.updateProvider(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      setEditDialogOpen(false);
      setSelectedProvider(null);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteProvider(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      setDeleteDialogOpen(false);
      setSelectedProvider(null);
    },
  });

  // Delete document mutation
  const deleteDocMutation = useMutation({
    mutationFn: (docId: string) => api.deleteDocument(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hospital-documents'] });
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      type: '',
      department: '',
      specialty: '',
      bio: '',
    });
    setAvailability({
      monday: { enabled: false, start: '09:00', end: '17:00' },
      tuesday: { enabled: false, start: '09:00', end: '17:00' },
      wednesday: { enabled: false, start: '09:00', end: '17:00' },
      thursday: { enabled: false, start: '09:00', end: '17:00' },
      friday: { enabled: false, start: '09:00', end: '17:00' },
      saturday: { enabled: false, start: '09:00', end: '17:00' },
      sunday: { enabled: false, start: '09:00', end: '17:00' },
    });
  };

  const handleCreate = () => {
    resetForm();
    setCreateDialogOpen(true);
  };

  const handleEdit = (provider: any) => {
    setSelectedProvider(provider);
    setFormData({
      name: provider.name,
      type: provider.type,
      department: provider.department,
      specialty: provider.specialty || '',
      bio: provider.bio || '',
    });
    setEditDialogOpen(true);
  };

  const handleDelete = (provider: any) => {
    setSelectedProvider(provider);
    setDeleteDialogOpen(true);
  };

  const handleCreateSubmit = () => {
    const availability_schedule = Object.entries(availability)
      .filter(([_, config]) => config.enabled)
      .map(([day, config]) => ({
        day_of_week: day,
        start_time: config.start,
        end_time: config.end,
      }));

    createMutation.mutate({
      name: formData.name,
      type: formData.type,
      department: formData.department,
      specialty: formData.specialty || null,
      bio: formData.bio || null,
      availability_schedule,
    });
  };

  const handleUpdateSubmit = () => {
    if (!selectedProvider) return;
    updateMutation.mutate({
      id: selectedProvider.id,
      data: {
        name: formData.name,
        type: formData.type,
        department: formData.department,
        specialty: formData.specialty || null,
        bio: formData.bio || null,
      },
    });
  };

  const handleDeleteConfirm = () => {
    if (!selectedProvider) return;
    deleteMutation.mutate(selectedProvider.id);
  };

  const filteredProviders = providers?.filter((provider: any) =>
    searchQuery === '' ||
    provider.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    provider.department?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    provider.specialty?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleViewDetails = (provider: any) => {
    setSelectedProvider(provider);
    setDetailsDialogOpen(true);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'doctor': return { bg: alpha('#2e7d32', 0.1), color: '#2e7d32' };
      case 'surgeon': return { bg: alpha('#1976d2', 0.1), color: '#1976d2' };
      case 'specialist': return { bg: alpha('#9c27b0', 0.1), color: '#9c27b0' };
      case 'nurse': return { bg: alpha('#ed6c02', 0.1), color: '#ed6c02' };
      case 'consultant': return { bg: alpha('#0288d1', 0.1), color: '#0288d1' };
      default: return { bg: alpha('#666', 0.1), color: '#666' };
    }
  };

  // Stats calculations
  const stats = {
    total: providers?.length || 0,
    departments: new Set(providers?.map((p: any) => p.department)).size || 0,
    doctors: providers?.filter((p: any) => p.type === 'doctor').length || 0,
    withSpecialty: providers?.filter((p: any) => p.specialty).length || 0,
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
          Provider Management
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Manage healthcare providers, schedules, and hospital documents
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {[
          { label: 'Total Providers', value: stats.total, color: '#840132', icon: <PersonIcon /> },
          { label: 'Departments', value: stats.departments, color: '#1976d2', icon: <MedicalIcon /> },
          { label: 'Doctors', value: stats.doctors, color: '#2e7d32', icon: <HospitalIcon /> },
          { label: 'Specialists', value: stats.withSpecialty, color: '#ed6c02', icon: <ScheduleIcon /> },
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

      {/* Tabs */}
      <Paper sx={{ borderRadius: 3, mb: 3, border: '1px solid', borderColor: 'divider' }}>
        <Tabs
          value={tabValue}
          onChange={(_, v) => setTabValue(v)}
          sx={{
            px: 2,
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 600,
              minHeight: 56,
            },
            '& .Mui-selected': {
              color: BRAND_COLOR,
            },
            '& .MuiTabs-indicator': {
              bgcolor: BRAND_COLOR,
            },
          }}
        >
          <Tab icon={<PersonIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="Providers" />
          <Tab icon={<DocumentIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="Hospital Documents" />
        </Tabs>
      </Paper>

      {/* Tab Content - Providers */}
      {tabValue === 0 && (
        <>
          {/* Search and Filters */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleCreate}
                sx={{
                  bgcolor: BRAND_COLOR,
                  '&:hover': { bgcolor: '#5e0124' },
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  px: 3,
                }}
              >
                Add Provider
              </Button>
              <TextField
                placeholder="Search by name, department, or specialty..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                size="small"
                sx={{ flex: 1, minWidth: 280 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon sx={{ color: '#999' }} />
                    </InputAdornment>
                  ),
                  sx: { borderRadius: 2 },
                }}
              />
              <TextField
                select
                label="Department"
                value={departmentFilter}
                onChange={(e) => setDepartmentFilter(e.target.value)}
                size="small"
                sx={{ minWidth: 180, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="">All Departments</MenuItem>
                {DEPARTMENTS.map((dept) => (
                  <MenuItem key={dept} value={dept}>{dept}</MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Type"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                size="small"
                sx={{ minWidth: 150, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="doctor">Doctor</MenuItem>
                <MenuItem value="nurse">Nurse</MenuItem>
                <MenuItem value="specialist">Specialist</MenuItem>
                <MenuItem value="surgeon">Surgeon</MenuItem>
                <MenuItem value="consultant">Consultant</MenuItem>
              </TextField>
            </Box>
          </Paper>

          {/* Providers Table */}
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress sx={{ color: BRAND_COLOR }} />
            </Box>
          ) : (
            <Paper sx={{ borderRadius: 3, overflow: 'hidden', border: '1px solid', borderColor: 'divider' }}>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: alpha(BRAND_COLOR, 0.03) }}>
                      <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }}>Provider</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }}>Department</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }}>Specialty</TableCell>
                      <TableCell sx={{ fontWeight: 700, color: '#1a1a1a', py: 2 }} align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredProviders && filteredProviders.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} align="center" sx={{ py: 8, color: '#666' }}>
                          No providers found
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredProviders?.map((provider: any) => {
                        const typeStyle = getTypeColor(provider.type);
                        return (
                          <TableRow key={provider.id} hover sx={{ '&:hover': { bgcolor: alpha(BRAND_COLOR, 0.02) } }}>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Avatar
                                  sx={{
                                    bgcolor: alpha(BRAND_COLOR, 0.1),
                                    color: BRAND_COLOR,
                                    fontWeight: 600,
                                  }}
                                >
                                  {provider.name.charAt(0)}
                                </Avatar>
                                <Box>
                                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#1a1a1a' }}>
                                    {provider.name}
                                  </Typography>
                                  <Typography variant="caption" sx={{ color: '#666' }}>
                                    ID: #{provider.id}
                                  </Typography>
                                </Box>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={provider.type}
                                size="small"
                                sx={{
                                  bgcolor: typeStyle.bg,
                                  color: typeStyle.color,
                                  fontWeight: 600,
                                  textTransform: 'capitalize',
                                }}
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ color: '#1a1a1a' }}>
                                {provider.department}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ color: provider.specialty ? '#1a1a1a' : '#999' }}>
                                {provider.specialty || '—'}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              <Tooltip title="View Details">
                                <IconButton size="small" onClick={() => handleViewDetails(provider)} sx={{ color: BRAND_COLOR }}>
                                  <VisibilityIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Edit">
                                <IconButton size="small" onClick={() => handleEdit(provider)} sx={{ color: '#666' }}>
                                  <EditIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Delete">
                                <IconButton size="small" onClick={() => handleDelete(provider)} sx={{ color: '#d32f2f' }}>
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </TableCell>
                          </TableRow>
                        );
                      })
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}
        </>
      )}

      {/* Tab Content - Hospital Documents */}
      {tabValue === 1 && (
        <Box>
          {uploadSuccess && (
            <Alert
              severity="success"
              sx={{ mb: 3, borderRadius: 2 }}
              onClose={() => setUploadSuccess(false)}
            >
              Document uploaded and indexed successfully!
            </Alert>
          )}
          {uploadError && (
            <Alert
              severity="error"
              sx={{ mb: 3, borderRadius: 2 }}
              onClose={() => setUploadError(null)}
            >
              {uploadError}
            </Alert>
          )}

          {/* Upload Section */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: 2,
                  bgcolor: alpha(BRAND_COLOR, 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <UploadIcon sx={{ color: BRAND_COLOR }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1a1a1a', mb: 0.5 }}>
                  Upload Hospital Documents
                </Typography>
                <Typography variant="body2" sx={{ color: '#666' }}>
                  Upload general information, policies, facility guides, and other hospital documents.
                  These will be indexed for the AI assistant to answer patient questions.
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mt: 3 }}>
              <Button
                variant="outlined"
                component="label"
                sx={{
                  textTransform: 'none',
                  borderRadius: 2,
                  borderColor: 'divider',
                  color: '#666',
                  '&:hover': { borderColor: BRAND_COLOR, color: BRAND_COLOR },
                }}
              >
                {generalDocFile ? generalDocFile.name : 'Choose PDF File'}
                <input
                  type="file"
                  accept=".pdf"
                  hidden
                  onChange={(e) => setGeneralDocFile(e.target.files ? e.target.files[0] : null)}
                />
              </Button>
              <Button
                variant="contained"
                disabled={!generalDocFile}
                onClick={async () => {
                  if (!generalDocFile) return;
                  try {
                    setUploadError(null);
                    await api.uploadGeneralDocument(generalDocFile, 'general');
                    queryClient.invalidateQueries({ queryKey: ['hospital-documents'] });
                    setGeneralDocFile(null);
                    setUploadSuccess(true);
                  } catch (err: any) {
                    console.error('general doc upload failed', err);
                    setUploadError(err.message || 'Failed to upload document');
                  }
                }}
                sx={{
                  bgcolor: BRAND_COLOR,
                  '&:hover': { bgcolor: '#5e0124' },
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                }}
              >
                Upload & Index
              </Button>
            </Box>
          </Paper>

          {/* Documents List */}
          <Paper sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#1a1a1a' }}>
                Indexed Documents
              </Typography>
              <Typography variant="body2" sx={{ color: '#666' }}>
                Documents available to the AI assistant
              </Typography>
            </Box>

            {documentsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                <CircularProgress sx={{ color: BRAND_COLOR }} />
              </Box>
            ) : documents && documents.length > 0 ? (
              <List sx={{ p: 0 }}>
                {documents.map((doc: any, index: number) => (
                  <ListItem
                    key={index}
                    sx={{
                      borderBottom: index < documents.length - 1 ? '1px solid' : 'none',
                      borderColor: 'divider',
                      py: 2,
                      px: 3,
                    }}
                  >
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: 2,
                        bgcolor: alpha('#1976d2', 0.1),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 2,
                      }}
                    >
                      <DocumentIcon sx={{ color: '#1976d2' }} />
                    </Box>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#1a1a1a' }}>
                          {doc.title || doc.metadata?.source || `Document ${index + 1}`}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ mt: 0.5, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                          {doc.metadata?.doc_type && (
                            <Chip label={doc.metadata.doc_type} size="small" sx={{ height: 22, fontSize: 11 }} />
                          )}
                          {doc.metadata?.department && (
                            <Chip label={doc.metadata.department} size="small" sx={{ height: 22, fontSize: 11 }} />
                          )}
                          <Typography variant="caption" sx={{ color: '#666' }}>
                            {doc.chunks || 0} chunks indexed
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Delete Document">
                        <IconButton
                          edge="end"
                          onClick={() => {
                            if (window.confirm('Are you sure you want to delete this document?')) {
                              deleteDocMutation.mutate(doc.id || String(index));
                            }
                          }}
                          disabled={deleteDocMutation.isPending}
                          sx={{ color: '#d32f2f' }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ py: 6, textAlign: 'center' }}>
                <DocumentIcon sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
                <Typography variant="body2" sx={{ color: '#666' }}>
                  No documents uploaded yet
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      )}

      {/* Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="sm" fullWidth>
        {selectedProvider && (
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
                  {selectedProvider.name.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {selectedProvider.name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    {selectedProvider.type} • {selectedProvider.department}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#666' }}>Provider ID</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>#{selectedProvider.id}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#666' }}>Type</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    <Chip label={selectedProvider.type} size="small" sx={getTypeColor(selectedProvider.type)} />
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#666' }}>Department</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedProvider.department}</Typography>
                </Grid>
                {selectedProvider.specialty && (
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#666' }}>Specialty</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedProvider.specialty}</Typography>
                  </Grid>
                )}
                {selectedProvider.bio && (
                  <Grid item xs={12}>
                    <Typography variant="caption" sx={{ color: '#666' }}>Bio</Typography>
                    <Paper
                      variant="outlined"
                      sx={{ p: 2, mt: 0.5, borderRadius: 2, bgcolor: alpha(BRAND_COLOR, 0.02) }}
                    >
                      <Typography variant="body2">{selectedProvider.bio}</Typography>
                    </Paper>
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Typography variant="caption" sx={{ color: '#666' }}>Created</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {new Date(selectedProvider.created_at).toLocaleDateString('en-US', {
                      year: 'numeric', month: 'long', day: 'numeric'
                    })}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={async () => {
                        try {
                          const blob = await api.downloadProviderPDF(selectedProvider.id);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `${selectedProvider.name.replace(/\s+/g, '_')}_Profile.pdf`;
                          document.body.appendChild(a);
                          a.click();
                          window.URL.revokeObjectURL(url);
                          document.body.removeChild(a);
                        } catch (err) {
                          console.error('Failed to download PDF:', err);
                          alert('Failed to download provider PDF');
                        }
                      }}
                      sx={{
                        borderColor: BRAND_COLOR,
                        color: BRAND_COLOR,
                        textTransform: 'none',
                        borderRadius: 2,
                        '&:hover': { borderColor: BRAND_COLOR, bgcolor: alpha(BRAND_COLOR, 0.05) },
                      }}
                    >
                      Download Provider PDF
                    </Button>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<UploadIcon />}
                      sx={{
                        textTransform: 'none',
                        borderRadius: 2,
                        borderColor: 'divider',
                        color: '#666',
                        '&:hover': { borderColor: '#2e7d32', color: '#2e7d32' },
                      }}
                    >
                      Upload New Document
                      <input
                        type="file"
                        accept=".pdf"
                        hidden
                        onChange={async (e) => {
                          const file = e.target.files?.[0];
                          if (!file) return;
                          try {
                            await api.uploadPDF(file, 'provider', selectedProvider.id);
                            alert('Document uploaded and indexed successfully!');
                          } catch (err) {
                            console.error('Upload failed:', err);
                            alert('Failed to upload document');
                          }
                        }}
                      />
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions sx={{ px: 3, py: 2 }}>
              <Button onClick={() => setDetailsDialogOpen(false)} sx={{ textTransform: 'none' }}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Create/Edit Dialog */}
      <Dialog
        open={createDialogOpen || editDialogOpen}
        onClose={() => {
          setCreateDialogOpen(false);
          setEditDialogOpen(false);
          resetForm();
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ fontWeight: 600 }}>
          {createDialogOpen ? 'Add New Provider' : 'Edit Provider'}
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2.5}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Type"
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                required
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="doctor">Doctor</MenuItem>
                <MenuItem value="nurse">Nurse</MenuItem>
                <MenuItem value="specialist">Specialist</MenuItem>
                <MenuItem value="surgeon">Surgeon</MenuItem>
                <MenuItem value="consultant">Consultant</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Department"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                required
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="">Select Department</MenuItem>
                {DEPARTMENTS.map((dept) => (
                  <MenuItem key={dept} value={dept}>{dept}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Specialty"
                value={formData.specialty}
                onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                placeholder="e.g., Pediatric Cardiology"
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Bio"
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                placeholder="Brief professional bio..."
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
            </Grid>

            {/* Weekly Availability */}
            {createDialogOpen && (
              <>
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mt: 1 }}>
                    Weekly Availability
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#666', mb: 2 }}>
                    Set working hours for each day (30-minute appointment slots)
                  </Typography>
                </Grid>
                {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day) => (
                  <Grid item xs={12} key={day}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={availability[day].enabled}
                            onChange={(e) => {
                              setAvailability({
                                ...availability,
                                [day]: { ...availability[day], enabled: e.target.checked },
                              });
                            }}
                            sx={{
                              '& .MuiSwitch-switchBase.Mui-checked': { color: BRAND_COLOR },
                              '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { bgcolor: BRAND_COLOR },
                            }}
                          />
                        }
                        label={
                          <Typography sx={{ minWidth: 90, textTransform: 'capitalize', fontWeight: 500 }}>
                            {day}
                          </Typography>
                        }
                        sx={{ mr: 2 }}
                      />
                      {availability[day].enabled && (
                        <>
                          <TextField
                            type="time"
                            label="Start"
                            value={availability[day].start}
                            onChange={(e) => {
                              setAvailability({
                                ...availability,
                                [day]: { ...availability[day], start: e.target.value },
                              });
                            }}
                            size="small"
                            sx={{ width: 140, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                          />
                          <Typography sx={{ color: '#666' }}>to</Typography>
                          <TextField
                            type="time"
                            label="End"
                            value={availability[day].end}
                            onChange={(e) => {
                              setAvailability({
                                ...availability,
                                [day]: { ...availability[day], end: e.target.value },
                              });
                            }}
                            size="small"
                            sx={{ width: 140, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                          />
                        </>
                      )}
                    </Box>
                  </Grid>
                ))}
              </>
            )}

            {/* File Upload */}
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mt: 1 }}>
                Provider Document (Optional)
              </Typography>
              <Typography variant="body2" sx={{ color: '#666', mb: 2 }}>
                Upload a PDF with provider credentials and information
              </Typography>
              <Button
                variant="outlined"
                component="label"
                sx={{ textTransform: 'none', borderRadius: 2 }}
              >
                {selectedFile ? selectedFile.name : 'Choose PDF File'}
                <input
                  type="file"
                  accept=".pdf"
                  hidden
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                />
              </Button>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button
            onClick={() => {
              setCreateDialogOpen(false);
              setEditDialogOpen(false);
              resetForm();
            }}
            sx={{ textTransform: 'none' }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={createDialogOpen ? handleCreateSubmit : handleUpdateSubmit}
            disabled={
              createMutation.isPending ||
              updateMutation.isPending ||
              !formData.name ||
              !formData.type ||
              !formData.department
            }
            sx={{
              bgcolor: BRAND_COLOR,
              '&:hover': { bgcolor: '#5e0124' },
              textTransform: 'none',
              borderRadius: 2,
              fontWeight: 600,
              px: 3,
            }}
          >
            {createMutation.isPending || updateMutation.isPending
              ? 'Saving...'
              : createDialogOpen
              ? 'Create Provider'
              : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>Delete Provider</DialogTitle>
        <DialogContent>
          {selectedProvider && (
            <Typography sx={{ color: '#666' }}>
              Are you sure you want to delete <strong>{selectedProvider.name}</strong> from{' '}
              <strong>{selectedProvider.department}</strong>? This action cannot be undone.
            </Typography>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setDeleteDialogOpen(false)} sx={{ textTransform: 'none' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteConfirm}
            disabled={deleteMutation.isPending}
            sx={{ textTransform: 'none', borderRadius: 2, fontWeight: 600 }}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
