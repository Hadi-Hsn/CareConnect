import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  CircularProgress,
} from '@mui/material';
import { api } from '@/lib/api';

export default function LabsPage() {
  const { data: labs, isLoading } = useQuery({
    queryKey: ['labs'],
    queryFn: () => api.getLabTests(),
  });

  if (isLoading) return <CircularProgress />;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Lab Tests
      </Typography>
      <Grid container spacing={3}>
        {labs?.map((lab) => (
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
