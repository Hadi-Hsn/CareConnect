import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Tab,
  Tabs,
  Button,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import { Database as DatabaseIcon, Warning as WarningIcon } from '@mui/icons-material';
import { api } from '@/lib/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return value === index ? <Box sx={{ p: 3 }}>{children}</Box> : null;
}

export default function AdminPage() {
  const [tabValue, setTabValue] = useState(0);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [populateSuccess, setPopulateSuccess] = useState(false);
  const [populateError, setPopulateError] = useState<string | null>(null);

  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => api.getKPIs(),
  });

  const populateMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/v1/admin/populate-database', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to populate database');
      }
      
      return response.json();
    },
    onSuccess: () => {
      setPopulateSuccess(true);
      setPopulateError(null);
      setConfirmDialogOpen(false);
      // Reload the page after 2 seconds to show new data
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    },
    onError: (error: Error) => {
      setPopulateError(error.message);
      setPopulateSuccess(false);
      setConfirmDialogOpen(false);
    },
  });

  const handlePopulateClick = () => {
    setConfirmDialogOpen(true);
    setPopulateSuccess(false);
    setPopulateError(null);
  };

  const handleConfirmPopulate = () => {
    populateMutation.mutate();
  };

  const handleCancelPopulate = () => {
    setConfirmDialogOpen(false);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Admin Dashboard
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<DatabaseIcon />}
          onClick={handlePopulateClick}
          disabled={populateMutation.isPending}
        >
          {populateMutation.isPending ? 'Populating...' : 'Populate Database'}
        </Button>
      </Box>

      {populateSuccess && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setPopulateSuccess(false)}>
          Database populated successfully! Page will reload shortly...
        </Alert>
      )}

      {populateError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setPopulateError(null)}>
          Failed to populate database: {populateError}
        </Alert>
      )}

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Metrics" />
        <Tab label="System Status" />
      </Tabs>
      <TabPanel value={tabValue} index={0}>
        {kpis && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Task Completion
                  </Typography>
                  <Typography variant="h3" color="primary">
                    {(kpis.task_completion_rate * 100).toFixed(1)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Avg Response Time
                  </Typography>
                  <Typography variant="h3" color="primary">
                    {kpis.avg_response_time_p50.toFixed(1)}s
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    p50: {kpis.avg_response_time_p50.toFixed(1)}s | p90: {kpis.avg_response_time_p90.toFixed(1)}s
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Satisfaction Score
                  </Typography>
                  <Typography variant="h3" color="primary">
                    {kpis.avg_satisfaction_score.toFixed(1)}/5
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Total Conversations
                  </Typography>
                  <Typography variant="h3" color="primary">
                    {kpis.total_conversations}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <Typography variant="body1">System health metrics coming soon...</Typography>
      </TabPanel>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialogOpen} onClose={handleCancelPopulate}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon color="warning" />
            <Typography variant="h6">Populate Database with Demo Data?</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            This action will:
            <Box component="ul" sx={{ mt: 1, pl: 2 }}>
              <li>Delete all existing patients, appointments, and providers</li>
              <li>Preserve the admin account (admin@aub.com / Admin@123)</li>
              <li>Create 30 demo patient accounts</li>
              <li>Create 3+ doctors per department</li>
              <li>Create 22 lab tests</li>
              <li>Generate diverse appointments across time periods</li>
              <li>Index all documents for the AI assistant</li>
            </Box>
            <Box sx={{ mt: 2, p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
              <Typography variant="body2" color="warning.dark" fontWeight={600}>
                ⚠️ WARNING: This will permanently delete existing data!
              </Typography>
            </Box>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelPopulate} color="inherit">
            Cancel
          </Button>
          <Button
            onClick={handleConfirmPopulate}
            color="primary"
            variant="contained"
            disabled={populateMutation.isPending}
            startIcon={populateMutation.isPending ? <CircularProgress size={20} /> : <DatabaseIcon />}
          >
            {populateMutation.isPending ? 'Populating...' : 'Populate Database'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
