import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  Typography,
  CircularProgress,
} from '@mui/material';
import { api } from '@/lib/api';

export default function AppointmentsPage() {
  const { data: appointments, isLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: () => api.getAppointments({ user_id: 1 }),
  });

  if (isLoading) return <CircularProgress />;

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
                  <Chip label={appt.status} color={appt.status === 'confirmed' ? 'success' : 'default'} size="small" />
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
