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
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';
import { DEPARTMENTS } from '@/lib/constants';

export default function ProvidersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selectedProvider, setSelectedProvider] = useState<any>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    department: '',
    specialty: '',
    bio: '',
    availability_calendar_id: '',
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

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => api.createProvider(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      setCreateDialogOpen(false);
      resetForm();
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

  const resetForm = () => {
    setFormData({
      name: '',
      type: '',
      department: '',
      specialty: '',
      bio: '',
      availability_calendar_id: '',
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
      availability_calendar_id: provider.availability_calendar_id || '',
    });
    setEditDialogOpen(true);
  };

  const handleDelete = (provider: any) => {
    setSelectedProvider(provider);
    setDeleteDialogOpen(true);
  };

  const handleCreateSubmit = () => {
    createMutation.mutate({
      name: formData.name,
      type: formData.type,
      department: formData.department,
      specialty: formData.specialty || null,
      bio: formData.bio || null,
      availability_calendar_id: formData.availability_calendar_id || null,
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
        availability_calendar_id: formData.availability_calendar_id || null,
      },
    });
  };

  const handleDeleteConfirm = () => {
    if (!selectedProvider) return;
    deleteMutation.mutate(selectedProvider.id);
  };

  // Filter providers based on search query
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

  if (isLoading) return <CircularProgress />;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Healthcare Providers
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        View and manage all doctors and healthcare providers
      </Typography>

      {/* Add Button and Filters */}
      <Box sx={{ display: 'flex', gap: 2, my: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
          sx={{ bgcolor: '#840132', '&:hover': { bgcolor: '#5e0124' } }}
        >
          Add Provider
        </Button>
        <TextField
          fullWidth
          placeholder="Search by name, department, or specialty..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ flex: 1, minWidth: 300 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <TextField
          select
          label="Department"
          value={departmentFilter}
          onChange={(e) => setDepartmentFilter(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="">All Departments</MenuItem>
          {DEPARTMENTS.map((dept) => (
            <MenuItem key={dept} value={dept}>
              {dept}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          select
          label="Type"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          sx={{ minWidth: 180 }}
        >
          <MenuItem value="">All Types</MenuItem>
          <MenuItem value="doctor">Doctor</MenuItem>
          <MenuItem value="nurse">Nurse</MenuItem>
          <MenuItem value="specialist">Specialist</MenuItem>
          <MenuItem value="surgeon">Surgeon</MenuItem>
          <MenuItem value="consultant">Consultant</MenuItem>
        </TextField>
      </Box>

      {/* Providers Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Provider Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Specialty</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredProviders && filteredProviders.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No providers found
                </TableCell>
              </TableRow>
            ) : (
              filteredProviders?.map((provider: any) => (
                <TableRow key={provider.id} hover>
                  <TableCell>#{provider.id}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Avatar sx={{ bgcolor: '#840132' }}>
                        {provider.name.charAt(0)}
                      </Avatar>
                      <Typography variant="body2" fontWeight="medium">
                        {provider.name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip label={provider.type} size="small" />
                  </TableCell>
                  <TableCell>{provider.department}</TableCell>
                  <TableCell>{provider.specialty || '-'}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleViewDetails(provider)}
                      color="primary"
                      title="View Details"
                    >
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleEdit(provider)}
                      color="primary"
                      title="Edit"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(provider)}
                      color="error"
                      title="Delete"
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

      {/* Statistics */}
      <Grid container spacing={2} sx={{ mt: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Providers
              </Typography>
              <Typography variant="h4">{providers?.length || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Departments
              </Typography>
              <Typography variant="h4">{DEPARTMENTS.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Provider Types
              </Typography>
              <Typography variant="h4">5</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                With Specialty
              </Typography>
              <Typography variant="h4">
                {providers?.filter((p: any) => p.specialty).length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedProvider && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: '#840132', width: 56, height: 56 }}>
                  {selectedProvider.name.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="h6">{selectedProvider.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedProvider.type} • {selectedProvider.department}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Provider ID
                  </Typography>
                  <Typography variant="body2">#{selectedProvider.id}</Typography>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Type
                  </Typography>
                  <Chip label={selectedProvider.type} />
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Department
                  </Typography>
                  <Typography variant="body2">{selectedProvider.department}</Typography>
                </Grid>

                {selectedProvider.specialty && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Specialty
                    </Typography>
                    <Typography variant="body2">{selectedProvider.specialty}</Typography>
                  </Grid>
                )}

                {selectedProvider.bio && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Bio
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2">{selectedProvider.bio}</Typography>
                    </Paper>
                  </Grid>
                )}

                {selectedProvider.availability_calendar_id && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Calendar ID
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {selectedProvider.availability_calendar_id}
                    </Typography>
                  </Grid>
                )}

                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Created At
                  </Typography>
                  <Typography variant="body2">
                    {new Date(selectedProvider.created_at).toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </DialogContent>
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
        <DialogTitle>
          {createDialogOpen ? 'Add New Provider' : 'Edit Provider'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Type *"
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                required
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
                label="Department *"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                required
              >
                <MenuItem value="">Select Department</MenuItem>
                {DEPARTMENTS.map((dept) => (
                  <MenuItem key={dept} value={dept}>
                    {dept}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Specialty"
                value={formData.specialty}
                onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
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
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Availability Calendar ID"
                value={formData.availability_calendar_id}
                onChange={(e) =>
                  setFormData({ ...formData, availability_calendar_id: e.target.value })
                }
                placeholder="Optional calendar integration ID"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setCreateDialogOpen(false);
              setEditDialogOpen(false);
              resetForm();
            }}
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
            sx={{ bgcolor: '#840132', '&:hover': { bgcolor: '#5e0124' } }}
          >
            {createMutation.isPending || updateMutation.isPending
              ? 'Saving...'
              : createDialogOpen
              ? 'Create Provider'
              : 'Update Provider'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Provider</DialogTitle>
        <DialogContent>
          {selectedProvider && (
            <Typography>
              Are you sure you want to delete{' '}
              <strong>{selectedProvider.name}</strong> from{' '}
              <strong>{selectedProvider.department}</strong>?
              <br />
              <br />
              This action cannot be undone.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteConfirm}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete Provider'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
