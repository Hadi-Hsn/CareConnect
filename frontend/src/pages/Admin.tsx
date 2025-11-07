import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Tab,
  Tabs,
} from '@mui/material';
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

  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => api.getKPIs(),
  });

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
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
    </Box>
  );
}
