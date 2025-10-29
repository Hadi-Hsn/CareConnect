import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
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
  const [docTitle, setDocTitle] = useState('');
  const [docContent, setDocContent] = useState('');
  const queryClient = useQueryClient();

  const { data: stats } = useQuery({
    queryKey: ['rag-stats'],
    queryFn: () => api.getRAGStats(),
  });

  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => api.getKPIs(),
  });

  const indexMutation = useMutation({
    mutationFn: (docs: any) => api.indexDocuments(docs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rag-stats'] });
      setDocTitle('');
      setDocContent('');
    },
  });

  const handleIndexDocument = () => {
    if (!docTitle || !docContent) return;
    indexMutation.mutate([{ title: docTitle, content: docContent }]);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Index Documents" />
        <Tab label="Metrics" />
        <Tab label="System Status" />
      </Tabs>
      <TabPanel value={tabValue} index={0}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Index New Document
            </Typography>
            <TextField
              fullWidth
              label="Document Title"
              value={docTitle}
              onChange={(e) => setDocTitle(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={10}
              label="Document Content"
              value={docContent}
              onChange={(e) => setDocContent(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Button
              variant="contained"
              onClick={handleIndexDocument}
              disabled={indexMutation.isPending}
            >
              Index Document
            </Button>
          </CardContent>
        </Card>
        {stats && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Vector Store Stats
              </Typography>
              <Typography>Total Vectors: {stats.total_vectors}</Typography>
              <Typography>Unique Documents: {stats.unique_documents}</Typography>
            </CardContent>
          </Card>
        )}
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
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
      <TabPanel value={tabValue} index={2}>
        <Typography variant="body1">System health metrics coming soon...</Typography>
      </TabPanel>
    </Box>
  );
}
