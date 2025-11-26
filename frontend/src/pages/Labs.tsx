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
  Avatar,
  alpha,
  Fade,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Science as ScienceIcon,
  Timer as TimerIcon,
  RestaurantMenu as FastingIcon,
  LocalHospital as DepartmentIcon,
  Biotech as BiotechIcon,
  FilterList as FilterIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';
import { DEPARTMENTS } from '@/lib/constants';

// Lab Test Card Component
function LabTestCard({ lab, index }: { lab: any; index: number }) {
  return (
    <Fade in timeout={300 + index * 100}>
      <Card
        elevation={0}
        sx={{
          height: '100%',
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
        {/* Department Color Bar */}
        <Box
          sx={{
            height: 4,
            background: 'linear-gradient(90deg, #840132 0%, #5e0124 100%)',
          }}
        />
        
        <CardContent sx={{ p: 3 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2.5 }}>
            <Avatar
              sx={{
                width: 56,
                height: 56,
                bgcolor: alpha('#840132', 0.1),
                color: '#840132',
              }}
            >
              <BiotechIcon />
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary', lineHeight: 1.2, mb: 0.5 }}>
                {lab.name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={lab.code}
                  size="small"
                  sx={{
                    bgcolor: alpha('#840132', 0.1),
                    color: '#840132',
                    fontWeight: 700,
                    fontFamily: 'monospace',
                  }}
                />
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {lab.department}
                </Typography>
              </Box>
            </Box>
          </Box>
          
          {/* Description */}
          {lab.description && (
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2.5, lineHeight: 1.6 }}>
              {lab.description}
            </Typography>
          )}
          
          {/* Info Grid */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 2,
              p: 2,
              bgcolor: '#f8f9fa',
              borderRadius: 2,
              mb: lab.prep_instructions ? 2 : 0,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <TimerIcon sx={{ color: '#840132', fontSize: 20 }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.65rem' }}>
                  Duration
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {lab.estimated_duration_minutes} minutes
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <FastingIcon sx={{ color: lab.fasting_hours ? '#ed6c02' : '#2e7d32', fontSize: 20 }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.65rem' }}>
                  Fasting
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: lab.fasting_hours ? '#ed6c02' : '#2e7d32' }}>
                  {lab.fasting_hours ? `${lab.fasting_hours} hours` : 'Not required'}
                </Typography>
              </Box>
            </Box>
          </Box>
          
          {/* Preparation Instructions */}
          {lab.prep_instructions && (
            <Box
              sx={{
                p: 2,
                bgcolor: alpha('#1976d2', 0.05),
                borderRadius: 2,
                border: '1px dashed',
                borderColor: alpha('#1976d2', 0.2),
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <InfoIcon sx={{ color: '#1976d2', fontSize: 18 }} />
                <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 700, textTransform: 'uppercase' }}>
                  Preparation Instructions
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: 'text.primary', lineHeight: 1.5 }}>
                {lab.prep_instructions}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Fade>
  );
}

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

  // Statistics
  const stats = {
    total: labs?.length || 0,
    departments: DEPARTMENTS.length,
    fasting: labs?.filter((lab: any) => lab.fasting_hours).length || 0,
    avgDuration: labs && labs.length > 0
      ? Math.round(labs.reduce((sum: number, lab: any) => sum + lab.estimated_duration_minutes, 0) / labs.length)
      : 0,
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress sx={{ color: '#840132' }} />
      </Box>
    );
  }

  // Admin view - Table format with all details
  if (isAdmin) {
    return (
      <Box sx={{ maxWidth: 1400, mx: 'auto' }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 800, background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', mb: 1 }}>
            Lab Tests Catalog
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            Manage all available laboratory tests and their details
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {[
            { label: 'Total Tests', value: stats.total, color: '#840132', icon: <ScienceIcon /> },
            { label: 'Departments', value: stats.departments, color: '#1976d2', icon: <DepartmentIcon /> },
            { label: 'Require Fasting', value: stats.fasting, color: '#ed6c02', icon: <FastingIcon /> },
            { label: 'Avg Duration', value: `${stats.avgDuration} min`, color: '#2e7d32', icon: <TimerIcon /> },
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

        {/* Filters */}
        <Paper
          elevation={0}
          sx={{
            p: 2,
            mb: 3,
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            gap: 2,
            flexWrap: 'wrap',
          }}
        >
          <TextField
            placeholder="Search by name, code, or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            sx={{ flexGrow: 1, minWidth: 300 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
            }}
          />
          <TextField
            select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <FilterIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
                </InputAdornment>
              ),
            }}
          >
            <MenuItem value="">All Departments</MenuItem>
            {DEPARTMENTS.map((dept) => (
              <MenuItem key={dept} value={dept}>{dept}</MenuItem>
            ))}
          </TextField>
        </Paper>

        {/* Table */}
        <TableContainer
          component={Paper}
          elevation={0}
          sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', overflow: 'hidden' }}
        >
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: '#f8f9fa' }}>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>ID</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Code</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Test Name</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Department</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Duration</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Fasting</TableCell>
                <TableCell sx={{ fontWeight: 700, color: 'text.secondary' }}>Description</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredLabs && filteredLabs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} sx={{ py: 8, textAlign: 'center' }}>
                    <ScienceIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'text.secondary' }}>No lab tests found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredLabs?.map((lab: any) => (
                  <TableRow key={lab.id} hover sx={{ '&:hover': { bgcolor: alpha('#840132', 0.02) } }}>
                    <TableCell>
                      <Chip label={`#${lab.id}`} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={lab.code}
                        size="small"
                        sx={{
                          bgcolor: alpha('#840132', 0.1),
                          color: '#840132',
                          fontWeight: 700,
                          fontFamily: 'monospace',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {lab.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        {lab.department}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <TimerIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                        <Typography variant="body2">{lab.estimated_duration_minutes} min</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {lab.fasting_hours ? (
                        <Chip
                          icon={<FastingIcon sx={{ fontSize: '16px !important' }} />}
                          label={`${lab.fasting_hours}h required`}
                          size="small"
                          sx={{ bgcolor: alpha('#ed6c02', 0.1), color: '#ed6c02', fontWeight: 600 }}
                        />
                      ) : (
                        <Typography variant="body2" sx={{ color: '#2e7d32', fontWeight: 600 }}>
                          Not required
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Tooltip title={lab.description || 'No description'} arrow>
                        <Typography
                          variant="body2"
                          sx={{
                            color: 'text.secondary',
                            maxWidth: 250,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {lab.description || '-'}
                        </Typography>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  }

  // Patient view - Card format
  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', mb: 1 }}>
          Lab Tests
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Browse available laboratory tests and their preparation requirements
        </Typography>
      </Box>
      
      {/* Search */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 4,
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <TextField
          fullWidth
          placeholder="Search lab tests by name, code, or description..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          variant="standard"
          InputProps={{
            disableUnderline: true,
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
              </InputAdornment>
            ),
            sx: { fontSize: '1.1rem' },
          }}
        />
      </Paper>

      {/* Lab Tests Grid */}
      {(!filteredLabs || filteredLabs.length === 0) ? (
        <Paper elevation={0} sx={{ p: 6, borderRadius: 4, border: '1px solid', borderColor: 'divider', textAlign: 'center' }}>
          <ScienceIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 1 }}>No lab tests found</Typography>
          <Typography variant="body2" sx={{ color: 'text.disabled' }}>Try adjusting your search terms</Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredLabs.map((lab: any, index: number) => (
            <Grid item xs={12} md={6} key={lab.id}>
              <LabTestCard lab={lab} index={index} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
