import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  InputAdornment,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { api } from '@/lib/api';
import { DEPARTMENTS } from '@/lib/constants';

export default function LabsPage() {
  const currentUser = api.getCurrentUser();
  const isAdmin = currentUser?.role === 'admin' || currentUser?.role === 'staff';
  
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: labs, isLoading } = useQuery({
    queryKey: ['labs', departmentFilter],
    queryFn: () => api.getLabTests(departmentFilter ? { department: departmentFilter } : {}),
  });

  // Filter labs based on search query
  const filteredLabs = labs?.filter((lab: any) =>
    searchQuery === '' ||
    lab.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lab.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lab.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) return <CircularProgress />;

  // Admin view - Table format with all details
  if (isAdmin) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Lab Tests Catalog
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Manage all available lab tests and their details
        </Typography>

        {/* Filters */}
        <Box sx={{ display: 'flex', gap: 2, my: 3 }}>
          <TextField
            fullWidth
            placeholder="Search by name, code, or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
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
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Code</TableCell>
                <TableCell>Test Name</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Fasting</TableCell>
                <TableCell>Description</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredLabs && filteredLabs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No lab tests found
                  </TableCell>
                </TableRow>
              ) : (
                filteredLabs?.map((lab: any) => (
                  <TableRow key={lab.id} hover>
                    <TableCell>#{lab.id}</TableCell>
                    <TableCell>
                      <Chip label={lab.code} size="small" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {lab.name}
                      </Typography>
                    </TableCell>
                    <TableCell>{lab.department}</TableCell>
                    <TableCell>{lab.estimated_duration_minutes} min</TableCell>
                    <TableCell>
                      {lab.fasting_hours ? (
                        <Chip
                          label={`${lab.fasting_hours}h`}
                          color="warning"
                          size="small"
                        />
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ maxWidth: 300 }}>
                        {lab.description || '-'}
                      </Typography>
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
                  Total Tests
                </Typography>
                <Typography variant="h4">{labs?.length || 0}</Typography>
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
                  Require Fasting
                </Typography>
                <Typography variant="h4">
                  {labs?.filter((lab: any) => lab.fasting_hours).length || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Avg Duration
                </Typography>
                <Typography variant="h4">
                  {labs && labs.length > 0
                    ? Math.round(
                        labs.reduce((sum: number, lab: any) => sum + lab.estimated_duration_minutes, 0) /
                          labs.length
                      )
                    : 0}{' '}
                  min
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  }

  // Patient view - Card format
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Lab Tests
      </Typography>
      
      {/* Search for patients */}
      <TextField
        fullWidth
        placeholder="Search lab tests..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />

      <Grid container spacing={3}>
        {filteredLabs?.map((lab: any) => (
          <Grid item xs={12} md={6} key={lab.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{lab.name}</Typography>
                <Chip label={lab.code} size="small" sx={{ mt: 1 }} />
                <Typography color="text.secondary" sx={{ mt: 1 }}>
                  {lab.department}
                </Typography>
                {lab.description && (
                  <Typography variant="body2" sx={{ mt: 2 }}>
                    {lab.description}
                  </Typography>
                )}
                {lab.prep_instructions && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Preparation Instructions:
                    </Typography>
                    <Typography variant="body2">{lab.prep_instructions}</Typography>
                  </Box>
                )}
                {lab.fasting_hours && (
                  <Chip
                    label={`Fasting: ${lab.fasting_hours} hours`}
                    color="warning"
                    size="small"
                    sx={{ mt: 1 }}
                  />
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
