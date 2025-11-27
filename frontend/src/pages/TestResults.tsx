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
  TextField,
  MenuItem,
  InputAdornment,
  Avatar,
  alpha,
  Fade,
  Button,
  Dialog,
  DialogContent,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Science as ScienceIcon,
  Assignment as ResultIcon,
  PictureAsPdf as PdfIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  FilterList as FilterIcon,
  CheckCircle as CompletedIcon,
  Pending as PendingIcon,
  Close as CloseIcon,
  CalendarMonth as CalendarIcon,
  LocalHospital as ProviderIcon,
  Biotech as BiotechIcon,
  TrendingUp as TrendingIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { format, formatDistanceToNow } from 'date-fns';
import { api } from '@/lib/api';

interface TestResult {
  id: number;
  user_id: number;
  test_name: string;
  test_category: string;
  test_date: string;
  result_value: string | null;
  result_unit: string | null;
  reference_range: string | null;
  status: string;
  notes: string | null;
  has_pdf: boolean;
  pdf_filename: string | null;
  provider_name: string | null;
  provider_specialty: string | null;
  created_at: string;
  updated_at: string;
}

// Status configuration
const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  completed: { label: 'Completed', color: '#2e7d32' },
  pending: { label: 'Pending', color: '#ed6c02' },
  reviewed: { label: 'Reviewed', color: '#1976d2' },
};

// Category icons
const getCategoryIcon = (category: string) => {
  switch (category.toLowerCase()) {
    case 'blood':
    case 'hematology':
      return <BiotechIcon />;
    case 'imaging':
    case 'radiology':
      return <ViewIcon />;
    case 'cardiology':
      return <TrendingIcon />;
    default:
      return <ScienceIcon />;
  }
};

// Test Result Card Component
function TestResultCard({ 
  result, 
  index,
  onViewDetails,
  onDownloadPdf,
}: { 
  result: TestResult; 
  index: number;
  onViewDetails: (result: TestResult) => void;
  onDownloadPdf: (resultId: number, filename: string) => void;
}) {
  const statusConfig = STATUS_CONFIG[result.status] || STATUS_CONFIG.pending;
  
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
          cursor: 'pointer',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(0,0,0,0.1)',
            borderColor: 'transparent',
          },
        }}
        onClick={() => onViewDetails(result)}
      >
        {/* Status Color Bar */}
        <Box
          sx={{
            height: 4,
            background: `linear-gradient(90deg, ${statusConfig.color} 0%, ${alpha(statusConfig.color, 0.6)} 100%)`,
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
              {getCategoryIcon(result.test_category)}
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography 
                variant="h6" 
                sx={{ 
                  fontWeight: 700, 
                  color: 'text.primary', 
                  lineHeight: 1.2, 
                  mb: 0.5,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {result.test_name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={result.test_category}
                  size="small"
                  sx={{
                    bgcolor: alpha('#840132', 0.1),
                    color: '#840132',
                    fontWeight: 600,
                    fontSize: '0.7rem',
                  }}
                />
                <Chip
                  label={statusConfig.label}
                  size="small"
                  sx={{
                    bgcolor: alpha(statusConfig.color, 0.1),
                    color: statusConfig.color,
                    fontWeight: 600,
                    fontSize: '0.7rem',
                  }}
                />
              </Box>
            </Box>
          </Box>
          
          {/* Test Date */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              p: 2,
              bgcolor: '#f8f9fa',
              borderRadius: 2,
              mb: 2,
            }}
          >
            <CalendarIcon sx={{ color: '#840132', fontSize: 20 }} />
            <Box>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.65rem' }}>
                Test Date
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {format(new Date(result.test_date), 'MMM dd, yyyy')}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {formatDistanceToNow(new Date(result.test_date), { addSuffix: true })}
              </Typography>
            </Box>
          </Box>
          
          {/* Provider Info */}
          {result.provider_name && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
              <ProviderIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {result.provider_name}
                </Typography>
                {result.provider_specialty && (
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    {result.provider_specialty}
                  </Typography>
                )}
              </Box>
            </Box>
          )}
          
          {/* Result Value if available */}
          {result.result_value && (
            <Box
              sx={{
                p: 2,
                bgcolor: alpha('#1976d2', 0.05),
                borderRadius: 2,
                border: '1px dashed',
                borderColor: alpha('#1976d2', 0.2),
                mb: 2,
              }}
            >
              <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 700, textTransform: 'uppercase' }}>
                Result
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 700, color: 'text.primary' }}>
                {result.result_value} {result.result_unit}
              </Typography>
              {result.reference_range && (
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Reference: {result.reference_range}
                </Typography>
              )}
            </Box>
          )}
          
          {/* Actions */}
          <Box sx={{ display: 'flex', gap: 1, mt: 'auto' }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<ViewIcon />}
              onClick={(e) => {
                e.stopPropagation();
                onViewDetails(result);
              }}
              sx={{
                flex: 1,
                borderColor: '#840132',
                color: '#840132',
                '&:hover': {
                  borderColor: '#5e0124',
                  bgcolor: alpha('#840132', 0.05),
                },
              }}
            >
              View Details
            </Button>
            {result.has_pdf && (
              <Tooltip title="Download PDF Report">
                <Button
                  variant="contained"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDownloadPdf(result.id, result.pdf_filename || `test_result_${result.id}.pdf`);
                  }}
                  sx={{
                    minWidth: 44,
                    bgcolor: '#840132',
                    '&:hover': { bgcolor: '#5e0124' },
                  }}
                >
                  <PdfIcon />
                </Button>
              </Tooltip>
            )}
          </Box>
        </CardContent>
      </Card>
    </Fade>
  );
}

// Details Dialog Component
function TestResultDetailsDialog({
  result,
  open,
  onClose,
  onDownloadPdf,
}: {
  result: TestResult | null;
  open: boolean;
  onClose: () => void;
  onDownloadPdf: (resultId: number, filename: string) => void;
}) {
  if (!result) return null;
  
  const statusConfig = STATUS_CONFIG[result.status] || STATUS_CONFIG.pending;
  
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 3, overflow: 'hidden' },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 3,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              sx={{
                width: 56,
                height: 56,
                bgcolor: alpha('#840132', 0.1),
                color: '#840132',
              }}
            >
              {getCategoryIcon(result.test_category)}
            </Avatar>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
                {result.test_name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                <Chip
                  label={result.test_category}
                  size="small"
                  sx={{
                    bgcolor: alpha('#840132', 0.1),
                    color: '#840132',
                    fontWeight: 600,
                  }}
                />
                <Chip
                  label={statusConfig.label}
                  size="small"
                  sx={{
                    bgcolor: alpha(statusConfig.color, 0.1),
                    color: statusConfig.color,
                    fontWeight: 600,
                  }}
                />
              </Box>
            </Box>
          </Box>
          <IconButton onClick={onClose} sx={{ color: 'text.secondary' }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </Box>
      
      <DialogContent sx={{ p: 3 }}>
        {/* Test Information */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: 'text.secondary', mb: 1.5, fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem' }}>
            Test Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box sx={{ p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                  Test Date
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {format(new Date(result.test_date), 'MMMM dd, yyyy')}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                  Category
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {result.test_category}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>
        
        {/* Provider Info */}
        {result.provider_name && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ color: 'text.secondary', mb: 1.5, fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem' }}>
              Ordered By
            </Typography>
            <Box sx={{ p: 2, bgcolor: alpha('#840132', 0.05), borderRadius: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: '#840132' }}>
                <ProviderIcon />
              </Avatar>
              <Box>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {result.provider_name}
                </Typography>
                {result.provider_specialty && (
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    {result.provider_specialty}
                  </Typography>
                )}
              </Box>
            </Box>
          </Box>
        )}
        
        {/* Results */}
        {result.result_value && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ color: 'text.secondary', mb: 1.5, fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem' }}>
              Test Results
            </Typography>
            <Box
              sx={{
                p: 3,
                bgcolor: alpha('#1976d2', 0.05),
                borderRadius: 2,
                border: '1px solid',
                borderColor: alpha('#1976d2', 0.2),
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 1 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2' }}>
                  {result.result_value}
                </Typography>
                {result.result_unit && (
                  <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                    {result.result_unit}
                  </Typography>
                )}
              </Box>
              {result.reference_range && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <InfoIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Reference Range: {result.reference_range}
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        )}
        
        {/* Notes */}
        {result.notes && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ color: 'text.secondary', mb: 1.5, fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem' }}>
              Notes
            </Typography>
            <Box sx={{ p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
              <Typography variant="body2" sx={{ color: 'text.primary', lineHeight: 1.6 }}>
                {result.notes}
              </Typography>
            </Box>
          </Box>
        )}
        
        {/* PDF Download */}
        {result.has_pdf && (
          <Box>
            <Typography variant="subtitle2" sx={{ color: 'text.secondary', mb: 1.5, fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem' }}>
              Report
            </Typography>
            <Button
              variant="contained"
              fullWidth
              startIcon={<DownloadIcon />}
              onClick={() => onDownloadPdf(result.id, result.pdf_filename || `test_result_${result.id}.pdf`)}
              sx={{
                py: 1.5,
                bgcolor: '#840132',
                '&:hover': { bgcolor: '#5e0124' },
              }}
            >
              Download PDF Report
            </Button>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default function TestResultsPage() {
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResult, setSelectedResult] = useState<TestResult | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Fetch test results
  const { data: testResults, isLoading } = useQuery<TestResult[]>({
    queryKey: ['my-test-results', statusFilter, categoryFilter],
    queryFn: async () => {
      const filters: { status_filter?: string; category?: string } = {};
      if (statusFilter) filters.status_filter = statusFilter;
      if (categoryFilter) filters.category = categoryFilter;
      
      return api.getMyTestResults(filters);
    },
  });

  // Fetch categories
  const { data: categories } = useQuery<string[]>({
    queryKey: ['test-result-categories'],
    queryFn: async () => {
      try {
        return await api.getMyTestResultCategories();
      } catch {
        return [];
      }
    },
  });

  // Filter results based on search query
  const filteredResults = testResults?.filter((result) =>
    searchQuery === '' ||
    result.test_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    result.test_category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    result.provider_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle PDF download
  const handleDownloadPdf = async (resultId: number, filename: string) => {
    try {
      const blob = await api.downloadMyTestResultPdf(resultId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  // Handle view details
  const handleViewDetails = (result: TestResult) => {
    setSelectedResult(result);
    setDetailsOpen(true);
  };

  // Statistics
  const stats = {
    total: testResults?.length || 0,
    completed: testResults?.filter(r => r.status === 'completed').length || 0,
    pending: testResults?.filter(r => r.status === 'pending').length || 0,
    withPdf: testResults?.filter(r => r.has_pdf).length || 0,
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: 400, gap: 2 }}>
        <CircularProgress sx={{ color: '#840132' }} />
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Loading your test results...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <Avatar
            sx={{
              width: 48,
              height: 48,
              background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)',
            }}
          >
            <ResultIcon />
          </Avatar>
          <Box>
            <Typography 
              variant="h4" 
              sx={{ 
                fontWeight: 800, 
                background: 'linear-gradient(135deg, #840132 0%, #5e0124 100%)', 
                WebkitBackgroundClip: 'text', 
                WebkitTextFillColor: 'transparent',
              }}
            >
              My Test Results
            </Typography>
            <Typography variant="body1" sx={{ color: 'text.secondary' }}>
              View and download your laboratory test results and reports
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {[
          { label: 'Total Results', value: stats.total, color: '#840132', icon: <ResultIcon /> },
          { label: 'Completed', value: stats.completed, color: '#2e7d32', icon: <CompletedIcon /> },
          { label: 'Pending', value: stats.pending, color: '#ed6c02', icon: <PendingIcon /> },
          { label: 'With Reports', value: stats.withPdf, color: '#1976d2', icon: <PdfIcon /> },
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
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: stat.color,
                  transform: 'translateY(-2px)',
                },
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
          placeholder="Search by test name, category, or provider..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          sx={{ flexGrow: 1, minWidth: 250 }}
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
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          size="small"
          sx={{ minWidth: 160 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <FilterIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
              </InputAdornment>
            ),
          }}
        >
          <MenuItem value="">All Categories</MenuItem>
          {categories?.map((cat) => (
            <MenuItem key={cat} value={cat}>{cat}</MenuItem>
          ))}
        </TextField>
        <TextField
          select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          size="small"
          sx={{ minWidth: 140 }}
        >
          <MenuItem value="">All Status</MenuItem>
          <MenuItem value="completed">Completed</MenuItem>
          <MenuItem value="pending">Pending</MenuItem>
          <MenuItem value="reviewed">Reviewed</MenuItem>
        </TextField>
      </Paper>

      {/* Results Grid */}
      {filteredResults && filteredResults.length === 0 ? (
        <Paper
          elevation={0}
          sx={{
            p: 6,
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            textAlign: 'center',
          }}
        >
          <ResultIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 1 }}>
            No test results found
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.disabled' }}>
            {searchQuery || categoryFilter || statusFilter
              ? 'Try adjusting your filters'
              : 'Your test results will appear here when available'}
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredResults?.map((result, index) => (
            <Grid item xs={12} sm={6} lg={4} key={result.id}>
              <TestResultCard
                result={result}
                index={index}
                onViewDetails={handleViewDetails}
                onDownloadPdf={handleDownloadPdf}
              />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Details Dialog */}
      <TestResultDetailsDialog
        result={selectedResult}
        open={detailsOpen}
        onClose={() => {
          setDetailsOpen(false);
          setSelectedResult(null);
        }}
        onDownloadPdf={handleDownloadPdf}
      />
    </Box>
  );
}
