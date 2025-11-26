import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  InputAdornment,
  TextField,
  Typography,
  CircularProgress,
  Avatar,
  Collapse,
  IconButton,
  Fade,
  Divider,
  Paper,
  alpha,
  Dialog,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  LocalHospital as HospitalIcon,
  Person as PersonIcon,
  MedicalServices as MedicalIcon,
  Healing as HealingIcon,
  Psychology as PsychologyIcon,
  Visibility as VisionIcon,
  ChildCare as ChildIcon,
  Favorite as HeartIcon,
  Science as ScienceIcon,
  Biotech as BiotechIcon,
  Close as CloseIcon,
  Badge as BadgeIcon,
  WorkOutline as WorkIcon,
} from '@mui/icons-material';
import { api } from '@/lib/api';
import type { Provider } from '@/types/api';

// Department icons mapping
const departmentIcons: { [key: string]: React.ReactNode } = {
  'Cardiology': <HeartIcon />,
  'Dermatology': <HealingIcon />,
  'Emergency Medicine': <MedicalIcon />,
  'Endocrinology': <BiotechIcon />,
  'Gastroenterology': <HospitalIcon />,
  'General Surgery': <MedicalIcon />,
  'Hematology': <ScienceIcon />,
  'Infectious Disease': <BiotechIcon />,
  'Internal Medicine': <PersonIcon />,
  'Nephrology': <ScienceIcon />,
  'Neurology': <PsychologyIcon />,
  'Neurosurgery': <PsychologyIcon />,
  'Obstetrics and Gynecology': <ChildIcon />,
  'Oncology': <ScienceIcon />,
  'Ophthalmology': <VisionIcon />,
  'Orthopedics': <HealingIcon />,
  'Otolaryngology (ENT)': <PersonIcon />,
  'Pathology': <ScienceIcon />,
  'Pediatrics': <ChildIcon />,
  'Physical Medicine and Rehabilitation': <HealingIcon />,
  'Psychiatry': <PsychologyIcon />,
  'Pulmonology': <HospitalIcon />,
  'Radiology': <ScienceIcon />,
  'Rheumatology': <HealingIcon />,
  'Urology': <HospitalIcon />,
};

// Department colors for visual distinction
const departmentColors: { [key: string]: string } = {
  'Cardiology': '#e53935',
  'Dermatology': '#8e24aa',
  'Emergency Medicine': '#d32f2f',
  'Endocrinology': '#1e88e5',
  'Gastroenterology': '#43a047',
  'General Surgery': '#5e35b1',
  'Hematology': '#c62828',
  'Infectious Disease': '#00897b',
  'Internal Medicine': '#3949ab',
  'Nephrology': '#00acc1',
  'Neurology': '#7b1fa2',
  'Neurosurgery': '#6a1b9a',
  'Obstetrics and Gynecology': '#ec407a',
  'Oncology': '#6d4c41',
  'Ophthalmology': '#039be5',
  'Orthopedics': '#fb8c00',
  'Otolaryngology (ENT)': '#00bcd4',
  'Pathology': '#795548',
  'Pediatrics': '#ff7043',
  'Physical Medicine and Rehabilitation': '#26a69a',
  'Psychiatry': '#ab47bc',
  'Pulmonology': '#42a5f5',
  'Radiology': '#78909c',
  'Rheumatology': '#ef5350',
  'Urology': '#5c6bc0',
};

// Provider type badges
const providerTypeBadge = (type: string) => {
  const typeConfig: { [key: string]: { label: string; color: 'primary' | 'secondary' | 'success' | 'warning' | 'info' } } = {
    'physician': { label: 'Physician', color: 'primary' },
    'specialist': { label: 'Specialist', color: 'secondary' },
    'nurse_practitioner': { label: 'Nurse Practitioner', color: 'success' },
    'physician_assistant': { label: 'Physician Assistant', color: 'info' },
  };
  const config = typeConfig[type.toLowerCase()] || { label: type, color: 'primary' as const };
  return <Chip size="small" label={config.label} color={config.color} variant="outlined" />;
};

// Get initials from name
const getInitials = (name: string) => {
  const parts = name.replace(/^Dr\.\s*/i, '').split(' ');
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
  }
  return parts[0].substring(0, 2).toUpperCase();
};

// Provider Detail Dialog Component
function ProviderDetailDialog({ 
  provider, 
  open, 
  onClose,
  departmentColor,
}: { 
  provider: Provider | null; 
  open: boolean; 
  onClose: () => void;
  departmentColor: string;
}) {
  if (!provider) return null;
  
  const DeptIcon = departmentIcons[provider.department] || <HospitalIcon />;
  
  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          overflow: 'hidden',
        }
      }}
    >
      {/* Header with gradient background */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${departmentColor} 0%, ${alpha(departmentColor, 0.8)} 100%)`,
          color: 'white',
          position: 'relative',
          pt: 4,
          pb: 8,
          px: 3,
        }}
      >
        <IconButton
          onClick={onClose}
          sx={{
            position: 'absolute',
            top: 12,
            right: 12,
            color: 'white',
            bgcolor: alpha('#fff', 0.1),
            '&:hover': {
              bgcolor: alpha('#fff', 0.2),
            },
          }}
        >
          <CloseIcon />
        </IconButton>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, opacity: 0.9 }}>
          <Box sx={{ width: 20, height: 20 }}>{DeptIcon}</Box>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {provider.department}
          </Typography>
        </Box>
        
        <DialogTitle sx={{ p: 0, color: 'white' }}>
          <Typography variant="h4" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
            {provider.name}
          </Typography>
        </DialogTitle>
      </Box>
      
      {/* Avatar overlapping header and content */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: -6, position: 'relative', zIndex: 1 }}>
        <Avatar
          sx={{
            width: 100,
            height: 100,
            bgcolor: 'white',
            color: departmentColor,
            fontSize: '2rem',
            fontWeight: 700,
            border: `4px solid white`,
            boxShadow: `0 4px 20px ${alpha('#000', 0.15)}`,
          }}
        >
          {getInitials(provider.name)}
        </Avatar>
      </Box>
      
      <DialogContent sx={{ pt: 2, pb: 4, px: 3 }}>
        {/* Specialty and Type */}
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <Typography 
            variant="h6" 
            sx={{ 
              color: departmentColor, 
              fontWeight: 600,
              mb: 1,
            }}
          >
            {provider.specialty || 'General Practice'}
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            {providerTypeBadge(provider.type)}
          </Box>
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        {/* About Section */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <BadgeIcon sx={{ color: departmentColor, fontSize: 20 }} />
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'text.primary' }}>
              About
            </Typography>
          </Box>
          <Typography 
            variant="body1" 
            sx={{ 
              color: 'text.secondary',
              lineHeight: 1.8,
              textAlign: 'justify',
            }}
          >
            {provider.bio || 'No biography available.'}
          </Typography>
        </Box>
        
        {/* Details Grid */}
        <Box 
          sx={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, 1fr)', 
            gap: 2,
            p: 2,
            bgcolor: alpha(departmentColor, 0.04),
            borderRadius: 2,
          }}
        >
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <WorkIcon sx={{ color: departmentColor, fontSize: 18 }} />
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase' }}>
                Department
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
              {provider.department}
            </Typography>
          </Box>
          
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <MedicalIcon sx={{ color: departmentColor, fontSize: 18 }} />
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase' }}>
                Specialty
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
              {provider.specialty || 'General'}
            </Typography>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
}

// Provider Card Component
function ProviderCard({ 
  provider, 
  departmentColor,
  onClick,
}: { 
  provider: Provider; 
  departmentColor: string;
  onClick: () => void;
}) {
  return (
    <Card
      elevation={0}
      onClick={onClick}
      sx={{
        height: '100%',
        borderRadius: 2,
        border: '1px solid',
        borderColor: 'divider',
        borderLeft: `3px solid ${departmentColor}`,
        transition: 'all 0.2s ease-in-out',
        position: 'relative',
        overflow: 'hidden',
        bgcolor: 'background.paper',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: `0 4px 12px ${alpha('#000', 0.08)}`,
          borderColor: alpha(departmentColor, 0.4),
          '& .provider-avatar': {
            transform: 'scale(1.02)',
          },
        },
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
          <Avatar
            className="provider-avatar"
            sx={{
              width: 64,
              height: 64,
              bgcolor: alpha(departmentColor, 0.1),
              color: departmentColor,
              fontSize: '1.25rem',
              fontWeight: 700,
              border: `2px solid ${alpha(departmentColor, 0.3)}`,
              transition: 'all 0.3s ease',
            }}
          >
            {getInitials(provider.name)}
          </Avatar>
          
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                fontSize: '1.05rem',
                color: 'text.primary',
                lineHeight: 1.3,
                mb: 0.5,
              }}
            >
              {provider.name}
            </Typography>
            
            <Typography
              variant="body2"
              sx={{
                color: departmentColor,
                fontWeight: 600,
                fontSize: '0.85rem',
                mb: 1,
              }}
            >
              {provider.specialty || 'General Practice'}
            </Typography>
            
            {providerTypeBadge(provider.type)}
          </Box>
        </Box>
        
        {provider.bio && (
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              fontSize: '0.875rem',
              lineHeight: 1.6,
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              mt: 2,
              pt: 2,
              borderTop: '1px solid',
              borderColor: 'divider',
            }}
          >
            {provider.bio}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

// Department Section Component
function DepartmentSection({ 
  department, 
  providers, 
  isExpanded, 
  onToggle,
  index,
  onProviderClick,
}: { 
  department: string; 
  providers: Provider[]; 
  isExpanded: boolean; 
  onToggle: () => void;
  index: number;
  onProviderClick: (provider: Provider) => void;
}) {
  const departmentColor = departmentColors[department] || '#840132';
  const DeptIcon = departmentIcons[department] || <HospitalIcon />;
  
  return (
    <Fade in timeout={300 + index * 50}>
      <Paper
        elevation={0}
        sx={{
          mb: 3,
          borderRadius: 4,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: isExpanded ? alpha(departmentColor, 0.3) : 'divider',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: alpha(departmentColor, 0.4),
            boxShadow: `0 4px 20px ${alpha(departmentColor, 0.1)}`,
          },
        }}
      >
        {/* Department Header */}
        <Box
          onClick={onToggle}
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 2.5,
            cursor: 'pointer',
            background: isExpanded 
              ? `linear-gradient(135deg, ${alpha(departmentColor, 0.08)} 0%, ${alpha(departmentColor, 0.03)} 100%)`
              : 'transparent',
            transition: 'all 0.3s ease',
            '&:hover': {
              background: `linear-gradient(135deg, ${alpha(departmentColor, 0.1)} 0%, ${alpha(departmentColor, 0.05)} 100%)`,
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                bgcolor: alpha(departmentColor, 0.15),
                color: departmentColor,
              }}
            >
              {DeptIcon}
            </Avatar>
            
            <Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  color: 'text.primary',
                }}
              >
                {department}
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: 'text.secondary',
                  fontSize: '0.85rem',
                }}
              >
                {providers.length} {providers.length === 1 ? 'provider' : 'providers'}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              size="small"
              label={`${providers.length}`}
              sx={{
                bgcolor: alpha(departmentColor, 0.1),
                color: departmentColor,
                fontWeight: 700,
                minWidth: 32,
              }}
            />
            <IconButton
              size="small"
              sx={{
                color: departmentColor,
                transition: 'transform 0.3s ease',
                transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>
        </Box>
        
        {/* Providers Grid */}
        <Collapse in={isExpanded} timeout="auto">
          <Box sx={{ p: 2.5, pt: 0 }}>
            <Divider sx={{ mb: 2.5 }} />
            <Grid container spacing={2.5}>
              {providers.map((provider) => (
                <Grid item xs={12} sm={6} md={4} key={provider.id}>
                  <ProviderCard 
                    provider={provider} 
                    departmentColor={departmentColor}
                    onClick={() => onProviderClick(provider)}
                  />
                </Grid>
              ))}
            </Grid>
          </Box>
        </Collapse>
      </Paper>
    </Fade>
  );
}

export default function ProviderDirectoryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedDepartments, setExpandedDepartments] = useState<Set<string>>(new Set());
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Handle provider click to open dialog
  const handleProviderClick = (provider: Provider) => {
    setSelectedProvider(provider);
    setDialogOpen(true);
  };

  // Handle dialog close
  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  // Fetch all providers
  const { data: providers, isLoading } = useQuery({
    queryKey: ['providers-directory'],
    queryFn: () => api.getProviders(),
  });

  // Group providers by department
  const providersByDepartment = useMemo((): { [department: string]: Provider[] } => {
    if (!providers) return {};
    
    const grouped: { [department: string]: Provider[] } = {};
    
    providers.forEach((provider: Provider) => {
      const dept = provider.department || 'Other';
      if (!grouped[dept]) {
        grouped[dept] = [];
      }
      grouped[dept].push(provider);
    });
    
    // Sort departments alphabetically
    const sorted: { [department: string]: Provider[] } = {};
    Object.keys(grouped)
      .sort()
      .forEach((key) => {
        sorted[key] = grouped[key].sort((a, b) => a.name.localeCompare(b.name));
      });
    
    return sorted;
  }, [providers]);

  // Filter providers based on search
  const filteredDepartments = useMemo((): { [department: string]: Provider[] } => {
    if (!searchQuery.trim()) return providersByDepartment;
    
    const query = searchQuery.toLowerCase();
    const filtered: { [department: string]: Provider[] } = {};
    
    Object.entries(providersByDepartment).forEach(([dept, providerList]) => {
      const providers = providerList as Provider[];
      const matchingProviders = providers.filter(
        (p: Provider) =>
          p.name.toLowerCase().includes(query) ||
          p.specialty?.toLowerCase().includes(query) ||
          p.bio?.toLowerCase().includes(query) ||
          dept.toLowerCase().includes(query)
      );
      
      if (matchingProviders.length > 0) {
        filtered[dept] = matchingProviders;
      }
    });
    
    return filtered;
  }, [providersByDepartment, searchQuery]);

  // Toggle department expansion
  const toggleDepartment = (department: string) => {
    setExpandedDepartments((prev: Set<string>) => {
      const next = new Set(prev);
      if (next.has(department)) {
        next.delete(department);
      } else {
        next.add(department);
      }
      return next;
    });
  };

  // Expand all when searching
  const effectiveExpanded = searchQuery.trim()
    ? new Set(Object.keys(filteredDepartments))
    : expandedDepartments;

  // Count total providers
  const totalProviders = providers?.length || 0;
  const totalDepartments = Object.keys(providersByDepartment).length;

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto' }}>
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
          Provider Directory
        </Typography>
        <Typography
          variant="body1"
          sx={{ color: 'text.secondary', mb: 3 }}
        >
          Find the right healthcare provider for your needs
        </Typography>

        {/* Stats */}
        <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
          <Paper
            elevation={0}
            sx={{
              px: 3,
              py: 1.5,
              borderRadius: 3,
              bgcolor: alpha('#840132', 0.08),
              border: '1px solid',
              borderColor: alpha('#840132', 0.2),
            }}
          >
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#840132' }}>
              {totalProviders}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Healthcare Providers
            </Typography>
          </Paper>
          
          <Paper
            elevation={0}
            sx={{
              px: 3,
              py: 1.5,
              borderRadius: 3,
              bgcolor: alpha('#1976d2', 0.08),
              border: '1px solid',
              borderColor: alpha('#1976d2', 0.2),
            }}
          >
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#1976d2' }}>
              {totalDepartments}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Medical Departments
            </Typography>
          </Paper>
        </Box>

        {/* Search */}
        <TextField
          fullWidth
          placeholder="Search by name, specialty, or department..."
          value={searchQuery}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            maxWidth: 500,
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              bgcolor: 'background.paper',
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#840132',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#840132',
              },
            },
          }}
        />
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress sx={{ color: '#840132' }} />
        </Box>
      )}

      {/* Empty State */}
      {!isLoading && Object.keys(filteredDepartments).length === 0 && (
        <Paper
          elevation={0}
          sx={{
            p: 6,
            textAlign: 'center',
            borderRadius: 4,
            bgcolor: alpha('#840132', 0.03),
            border: '1px dashed',
            borderColor: alpha('#840132', 0.2),
          }}
        >
          <HospitalIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 1 }}>
            No providers found
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.disabled' }}>
            {searchQuery ? 'Try adjusting your search criteria' : 'No providers are currently available'}
          </Typography>
        </Paper>
      )}

      {/* Department Sections */}
      {!isLoading && Object.entries(filteredDepartments).map(([department, deptProviders], index) => (
        <DepartmentSection
          key={department}
          department={department}
          providers={deptProviders as Provider[]}
          isExpanded={effectiveExpanded.has(department)}
          onToggle={() => toggleDepartment(department)}
          index={index}
          onProviderClick={handleProviderClick}
        />
      ))}

      {/* Provider Detail Dialog */}
      <ProviderDetailDialog
        provider={selectedProvider}
        open={dialogOpen}
        onClose={handleDialogClose}
        departmentColor={selectedProvider ? (departmentColors[selectedProvider.department] || '#840132') : '#840132'}
      />
    </Box>
  );
}
