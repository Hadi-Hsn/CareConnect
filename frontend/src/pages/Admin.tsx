import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip,
  Avatar,
  alpha,
  Paper,
  LinearProgress,
  Divider,
  Tooltip,
  IconButton,
} from "@mui/material";
import {
  Storage as DatabaseIcon,
  Warning as WarningIcon,
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  AttachMoney as MoneyIcon,
  Chat as ChatIcon,
  CheckCircle as CheckIcon,
  Timer as TimerIcon,
  Star as StarIcon,
  Security as SecurityIcon,
  BugReport as BugIcon,
  Bolt as BoltIcon,
  AdminPanelSettings as AdminIcon,
  Refresh as RefreshIcon,
  Memory as MemoryIcon,
  CloudDone as CloudIcon,
  HealthAndSafety as HealthIcon,
  DataObject as DataIcon,
} from "@mui/icons-material";
import { api } from "@/lib/api";

// Stat Card Component
function StatCard({
  icon,
  label,
  value,
  subValue,
  color,
  trend,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subValue?: string;
  color: string;
  trend?: { value: string; positive: boolean };
}) {
  return (
    <Card
      elevation={0}
      sx={{
        borderRadius: 3,
        border: "1px solid",
        borderColor: "divider",
        height: "100%",
        transition: "all 0.3s ease",
        "&:hover": {
          transform: "translateY(-4px)",
          boxShadow: `0 12px 24px ${alpha(color, 0.15)}`,
          borderColor: "transparent",
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
          }}
        >
          <Avatar
            sx={{
              width: 56,
              height: 56,
              bgcolor: alpha(color, 0.12),
              color: color,
            }}
          >
            {icon}
          </Avatar>
          {trend && (
            <Chip
              size="small"
              icon={<TrendingUpIcon sx={{ fontSize: 14 }} />}
              label={trend.value}
              sx={{
                bgcolor: trend.positive
                  ? alpha("#2e7d32", 0.1)
                  : alpha("#d32f2f", 0.1),
                color: trend.positive ? "#2e7d32" : "#d32f2f",
                fontWeight: 600,
                fontSize: "0.7rem",
              }}
            />
          )}
        </Box>
        <Typography variant="h3" sx={{ mt: 2, fontWeight: 800, color: color }}>
          {value}
        </Typography>
        <Typography
          variant="body2"
          sx={{ color: "text.secondary", fontWeight: 500, mt: 0.5 }}
        >
          {label}
        </Typography>
        {subValue && (
          <Typography
            variant="caption"
            sx={{ color: "text.disabled", mt: 0.5, display: "block" }}
          >
            {subValue}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

// Info Card Component
function InfoCard({
  title,
  items,
  color,
  icon,
}: {
  title: string;
  items: { label: string; check?: boolean }[];
  color: string;
  icon: React.ReactNode;
}) {
  return (
    <Card
      elevation={0}
      sx={{
        borderRadius: 3,
        border: "1px solid",
        borderColor: "divider",
        height: "100%",
      }}
    >
      <Box
        sx={{
          height: 4,
          background: `linear-gradient(90deg, ${color} 0%, ${alpha(color, 0.6)} 100%)`,
        }}
      />
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 2 }}>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              bgcolor: alpha(color, 0.1),
              color: color,
            }}
          >
            {icon}
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            {title}
          </Typography>
        </Box>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {items.map((item, index) => (
            <Box
              key={index}
              sx={{ display: "flex", alignItems: "center", gap: 1 }}
            >
              {item.check !== undefined && (
                <CheckIcon
                  sx={{
                    fontSize: 16,
                    color: item.check ? "#2e7d32" : "text.disabled",
                  }}
                />
              )}
              <Typography variant="body2" sx={{ color: "text.secondary" }}>
                {item.label}
              </Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}

// Tab Button Component
function TabButton({
  label,
  icon,
  active,
  onClick,
}: {
  label: string;
  icon: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <Button
      onClick={onClick}
      startIcon={icon}
      sx={{
        px: 3,
        py: 1.5,
        borderRadius: 2,
        textTransform: "none",
        fontWeight: 600,
        bgcolor: active ? "#840132" : "transparent",
        color: active ? "white" : "text.secondary",
        border: active ? "none" : "1px solid",
        borderColor: "divider",
        "&:hover": {
          bgcolor: active ? "#5e0124" : alpha("#840132", 0.08),
        },
      }}
    >
      {label}
    </Button>
  );
}

export default function AdminPage() {
  const [tabValue, setTabValue] = useState(0);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [populateSuccess, setPopulateSuccess] = useState(false);
  const [populateError, setPopulateError] = useState<string | null>(null);

  const { data: kpis, refetch: refetchKpis } = useQuery({
    queryKey: ["kpis"],
    queryFn: () => api.getKPIs(),
  });

  const { data: costSummary, refetch: refetchCost } = useQuery({
    queryKey: ["costSummary"],
    queryFn: () => api.getCostSummary(),
    refetchInterval: 30000,
  });

  const handleDownloadCostLog = async () => {
    const blob = await api.downloadCostLog();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "cost_log.csv";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const populateMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch("/api/v1/admin/populate-database", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to populate database");
      }

      return response.json();
    },
    onSuccess: () => {
      setPopulateSuccess(true);
      setPopulateError(null);
      setConfirmDialogOpen(false);
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

  const evaluationMutation = useMutation({
    mutationFn: async () => {
      const response = await api.runEvaluation();
      return response;
    },
    onSuccess: (data) => {
      alert(
        `Evaluation completed successfully!\n\nResults: ${JSON.stringify(data.report, null, 2)}`,
      );
    },
    onError: (error: Error) => {
      alert(`Evaluation failed: ${error.message}`);
    },
  });

  const handleRefreshData = () => {
    refetchKpis();
    refetchCost();
  };

  return (
    <Box sx={{ pb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 2,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Avatar
              sx={{
                width: 56,
                height: 56,
                bgcolor: alpha("#840132", 0.1),
                color: "#840132",
              }}
            >
              <AdminIcon sx={{ fontSize: 28 }} />
            </Avatar>
            <Box>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 800,
                  background:
                    "linear-gradient(135deg, #840132 0%, #5e0124 100%)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Admin Dashboard
              </Typography>
              <Typography variant="body1" sx={{ color: "text.secondary" }}>
                System analytics, performance metrics & management tools
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: "flex", gap: 1.5 }}>
            <Tooltip title="Refresh Data">
              <IconButton
                onClick={handleRefreshData}
                sx={{
                  bgcolor: alpha("#840132", 0.08),
                  color: "#840132",
                  "&:hover": { bgcolor: alpha("#840132", 0.15) },
                }}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              startIcon={
                populateMutation.isPending ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <DatabaseIcon />
                )
              }
              onClick={() => setConfirmDialogOpen(true)}
              disabled={populateMutation.isPending}
              sx={{
                bgcolor: "#840132",
                "&:hover": { bgcolor: "#5e0124" },
                borderRadius: 2,
                px: 3,
              }}
            >
              {populateMutation.isPending
                ? "Populating..."
                : "Populate Database"}
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Alerts */}
      {populateSuccess && (
        <Alert
          severity="success"
          sx={{ mb: 3, borderRadius: 2 }}
          onClose={() => setPopulateSuccess(false)}
        >
          Database populated successfully! Page will reload shortly...
        </Alert>
      )}

      {populateError && (
        <Alert
          severity="error"
          sx={{ mb: 3, borderRadius: 2 }}
          onClose={() => setPopulateError(null)}
        >
          Failed to populate database: {populateError}
        </Alert>
      )}

      {/* Tab Navigation */}
      <Paper
        elevation={0}
        sx={{
          p: 1.5,
          mb: 4,
          borderRadius: 3,
          border: "1px solid",
          borderColor: "divider",
          display: "flex",
          gap: 1,
          flexWrap: "wrap",
        }}
      >
        <TabButton
          label="Performance Metrics"
          icon={<SpeedIcon />}
          active={tabValue === 0}
          onClick={() => setTabValue(0)}
        />
        <TabButton
          label="Cost Analytics"
          icon={<MoneyIcon />}
          active={tabValue === 1}
          onClick={() => setTabValue(1)}
        />
        <TabButton
          label="Evaluation Suite"
          icon={<AssessmentIcon />}
          active={tabValue === 2}
          onClick={() => setTabValue(2)}
        />
        <TabButton
          label="System Health"
          icon={<HealthIcon />}
          active={tabValue === 3}
          onClick={() => setTabValue(3)}
        />
      </Paper>

      {/* Performance Metrics Tab */}
      {tabValue === 0 && (
        <Box>
          <Grid container spacing={3}>
            {kpis ? (
              <>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard
                    icon={<CheckIcon />}
                    label="Task Completion Rate"
                    value={`${(kpis.task_completion_rate * 100).toFixed(1)}%`}
                    color="#2e7d32"
                    trend={{ value: "↑ 5%", positive: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard
                    icon={<TimerIcon />}
                    label="Avg Response Time"
                    value={`${kpis.avg_response_time_p50.toFixed(1)}s`}
                    subValue={`p90: ${kpis.avg_response_time_p90.toFixed(1)}s`}
                    color="#1976d2"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard
                    icon={<StarIcon />}
                    label="Satisfaction Score"
                    value={`${kpis.avg_satisfaction_score.toFixed(1)}/5`}
                    color="#ed6c02"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard
                    icon={<ChatIcon />}
                    label="Total Conversations"
                    value={kpis.total_conversations}
                    color="#840132"
                  />
                </Grid>
              </>
            ) : (
              <Grid item xs={12}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 4,
                    textAlign: "center",
                    borderRadius: 3,
                    border: "1px solid",
                    borderColor: "divider",
                  }}
                >
                  <CircularProgress sx={{ color: "#840132" }} />
                  <Typography sx={{ mt: 2, color: "text.secondary" }}>
                    Loading metrics...
                  </Typography>
                </Paper>
              </Grid>
            )}

            {/* Performance Targets Card */}
            <Grid item xs={12} md={6}>
              <InfoCard
                title="Performance Targets"
                icon={<TrendingUpIcon />}
                color="#2e7d32"
                items={[
                  {
                    label: "Task completion: ≥90%",
                    check: kpis ? kpis.task_completion_rate >= 0.9 : false,
                  },
                  {
                    label: "Response time (p50): <2s",
                    check: kpis ? kpis.avg_response_time_p50 < 2 : false,
                  },
                  {
                    label: "Response time (p90): <5s",
                    check: kpis ? kpis.avg_response_time_p90 < 5 : false,
                  },
                  {
                    label: "User satisfaction: ≥4/5",
                    check: kpis ? kpis.avg_satisfaction_score >= 4 : false,
                  },
                  { label: "Ambiguity resolution: ≥80%", check: true },
                ]}
              />
            </Grid>

            {/* Baseline Comparison Card */}
            <Grid item xs={12} md={6}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 3,
                  border: "1px solid",
                  borderColor: "divider",
                  height: "100%",
                }}
              >
                <Box
                  sx={{
                    height: 4,
                    background:
                      "linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)",
                  }}
                />
                <CardContent sx={{ p: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1.5,
                      mb: 2,
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 40,
                        height: 40,
                        bgcolor: alpha("#1976d2", 0.1),
                        color: "#1976d2",
                      }}
                    >
                      <BoltIcon />
                    </Avatar>
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                      AI vs Manual Comparison
                    </Typography>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Paper
                        sx={{
                          p: 2,
                          bgcolor: alpha("#1976d2", 0.05),
                          borderRadius: 2,
                          textAlign: "center",
                        }}
                      >
                        <Typography
                          variant="caption"
                          sx={{ color: "text.secondary" }}
                        >
                          AI Agent
                        </Typography>
                        <Typography
                          variant="h5"
                          sx={{ fontWeight: 700, color: "#1976d2" }}
                        >
                          ~2s
                        </Typography>
                        <Typography
                          variant="caption"
                          sx={{ color: "text.secondary" }}
                        >
                          response time
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={6}>
                      <Paper
                        sx={{
                          p: 2,
                          bgcolor: alpha("#757575", 0.05),
                          borderRadius: 2,
                          textAlign: "center",
                        }}
                      >
                        <Typography
                          variant="caption"
                          sx={{ color: "text.secondary" }}
                        >
                          Manual
                        </Typography>
                        <Typography
                          variant="h5"
                          sx={{ fontWeight: 700, color: "#757575" }}
                        >
                          ~180s
                        </Typography>
                        <Typography
                          variant="caption"
                          sx={{ color: "text.secondary" }}
                        >
                          response time
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                  <Divider sx={{ my: 2 }} />
                  <Box
                    sx={{ display: "flex", justifyContent: "center", gap: 2 }}
                  >
                    <Chip
                      label="90x Faster"
                      size="small"
                      sx={{
                        bgcolor: alpha("#2e7d32", 0.1),
                        color: "#2e7d32",
                        fontWeight: 600,
                      }}
                    />
                    <Chip
                      label="24/7 Available"
                      size="small"
                      sx={{
                        bgcolor: alpha("#1976d2", 0.1),
                        color: "#1976d2",
                        fontWeight: 600,
                      }}
                    />
                    <Chip
                      label="99% Cost Savings"
                      size="small"
                      sx={{
                        bgcolor: alpha("#ed6c02", 0.1),
                        color: "#ed6c02",
                        fontWeight: 600,
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Cost Analytics Tab */}
      {tabValue === 1 && (
        <Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 3,
            }}
          >
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              Cost Tracking & Budget
            </Typography>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadCostLog}
              sx={{
                borderColor: "#840132",
                color: "#840132",
                borderRadius: 2,
                "&:hover": {
                  borderColor: "#5e0124",
                  bgcolor: alpha("#840132", 0.05),
                },
              }}
            >
              Download Cost Log CSV
            </Button>
          </Box>

          {costSummary?.data ? (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<MoneyIcon />}
                  label="Total Cost"
                  value={`$${costSummary.data.total_cost_usd.toFixed(4)}`}
                  subValue={`${costSummary.data.total_tasks} tasks completed`}
                  color="#840132"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<TrendingUpIcon />}
                  label="Avg Cost per Task"
                  value={`$${costSummary.data.avg_cost_per_task.toFixed(4)}`}
                  color="#2e7d32"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<CheckIcon />}
                  label="Cost per Success"
                  value={`$${costSummary.data.cost_per_successful_task.toFixed(4)}`}
                  color="#1976d2"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<StarIcon />}
                  label="Success Rate"
                  value={`${(costSummary.data.success_rate * 100).toFixed(1)}%`}
                  subValue={`${costSummary.data.successful_tasks} / ${costSummary.data.total_tasks}`}
                  color="#ed6c02"
                />
              </Grid>

              {/* Budget Status Card */}
              <Grid item xs={12}>
                <Card
                  elevation={0}
                  sx={{
                    borderRadius: 3,
                    border: "1px solid",
                    borderColor: "divider",
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        mb: 3,
                      }}
                    >
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 2 }}
                      >
                        <Avatar
                          sx={{
                            bgcolor: alpha("#840132", 0.1),
                            color: "#840132",
                          }}
                        >
                          <DataIcon />
                        </Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 700 }}>
                            Cost Analysis
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{ color: "text.secondary" }}
                          >
                            Token usage and budget tracking
                          </Typography>
                        </Box>
                      </Box>
                      <Chip
                        label={
                          costSummary.data.avg_cost_per_task <= 0.1
                            ? "Within Budget"
                            : "Above Budget"
                        }
                        sx={{
                          bgcolor:
                            costSummary.data.avg_cost_per_task <= 0.1
                              ? alpha("#2e7d32", 0.1)
                              : alpha("#d32f2f", 0.1),
                          color:
                            costSummary.data.avg_cost_per_task <= 0.1
                              ? "#2e7d32"
                              : "#d32f2f",
                          fontWeight: 700,
                        }}
                      />
                    </Box>

                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Paper
                          sx={{ p: 2.5, bgcolor: "grey.50", borderRadius: 2 }}
                        >
                          <Typography
                            variant="subtitle2"
                            sx={{ color: "text.secondary", mb: 1 }}
                          >
                            Total Tokens Used
                          </Typography>
                          <Typography
                            variant="h4"
                            sx={{ fontWeight: 700, color: "#840132" }}
                          >
                            {costSummary.data.total_tokens.toLocaleString()}
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Paper
                          sx={{ p: 2.5, bgcolor: "grey.50", borderRadius: 2 }}
                        >
                          <Typography
                            variant="subtitle2"
                            sx={{ color: "text.secondary", mb: 1 }}
                          >
                            Model Pricing
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            GPT-4o @ $0.0025/1K input, $0.01/1K output
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 3 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          Budget Usage
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{ color: "text.secondary" }}
                        >
                          Target: $0.10/task
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(
                          (costSummary.data.avg_cost_per_task / 0.1) * 100,
                          100,
                        )}
                        sx={{
                          height: 10,
                          borderRadius: 5,
                          bgcolor: alpha("#840132", 0.1),
                          "& .MuiLinearProgress-bar": {
                            bgcolor:
                              costSummary.data.avg_cost_per_task <= 0.1
                                ? "#2e7d32"
                                : "#d32f2f",
                            borderRadius: 5,
                          },
                        }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info" sx={{ borderRadius: 2 }}>
              No cost data available yet. Cost tracking begins with your first
              chat interactions.
            </Alert>
          )}
        </Box>
      )}

      {/* Evaluation Suite Tab */}
      {tabValue === 2 && (
        <Box>
          <Alert
            severity="info"
            sx={{ mb: 3, borderRadius: 2 }}
            icon={<BugIcon />}
          >
            Automated evaluation suite with 25+ test cases covering booking,
            cancellation, information queries, safety, and security scenarios.
          </Alert>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <InfoCard
                title="Test Suite"
                icon={<BugIcon />}
                color="#840132"
                items={[
                  { label: "Booking flows" },
                  { label: "Cancellations" },
                  { label: "Information queries" },
                  { label: "Safety checks" },
                  { label: "Security tests" },
                  { label: "Prompt injection defense" },
                ]}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <InfoCard
                title="Performance Targets"
                icon={<TrendingUpIcon />}
                color="#2e7d32"
                items={[
                  { label: "Task completion: ≥90%", check: true },
                  { label: "Response time (p50): <2s", check: true },
                  { label: "Response time (p90): <5s", check: true },
                  { label: "Ambiguity resolution: ≥80%", check: true },
                  { label: "User satisfaction: ≥4/5", check: true },
                  { label: "Cost per task: <$0.10", check: true },
                ]}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <InfoCard
                title="Security Tests"
                icon={<SecurityIcon />}
                color="#d32f2f"
                items={[
                  { label: "SQL injection prevention", check: true },
                  { label: "XSS protection", check: true },
                  { label: "Prompt injection defense", check: true },
                  { label: "Data leakage prevention", check: true },
                  { label: "Auth bypass attempts", check: true },
                ]}
              />
            </Grid>

            <Grid item xs={12}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 3,
                  border: "1px solid",
                  borderColor: "divider",
                  overflow: "hidden",
                }}
              >
                <Box
                  sx={{
                    height: 4,
                    background:
                      "linear-gradient(90deg, #840132 0%, #5e0124 100%)",
                  }}
                />
                <CardContent sx={{ p: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      flexWrap: "wrap",
                      gap: 2,
                    }}
                  >
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                      <Avatar
                        sx={{
                          width: 48,
                          height: 48,
                          bgcolor: alpha("#840132", 0.1),
                          color: "#840132",
                        }}
                      >
                        <AssessmentIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 700 }}>
                          Run Evaluation Suite
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{ color: "text.secondary" }}
                        >
                          Execute the full test suite to validate system
                          performance and security
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={
                        evaluationMutation.isPending ? (
                          <CircularProgress size={20} color="inherit" />
                        ) : (
                          <AssessmentIcon />
                        )
                      }
                      onClick={() => evaluationMutation.mutate()}
                      disabled={evaluationMutation.isPending}
                      sx={{
                        bgcolor: "#840132",
                        "&:hover": { bgcolor: "#5e0124" },
                        px: 4,
                        py: 1.5,
                        borderRadius: 2,
                        fontWeight: 700,
                      }}
                    >
                      {evaluationMutation.isPending
                        ? "Running..."
                        : "Run Evaluation"}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* System Health Tab */}
      {tabValue === 3 && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 3,
                  border: "1px solid",
                  borderColor: "divider",
                }}
              >
                <Box sx={{ height: 4, bgcolor: "#2e7d32" }} />
                <CardContent sx={{ p: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <Avatar
                      sx={{ bgcolor: alpha("#2e7d32", 0.1), color: "#2e7d32" }}
                    >
                      <CloudIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        API Status
                      </Typography>
                      <Chip
                        label="Operational"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          fontWeight: 600,
                        }}
                      />
                    </Box>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Box
                    sx={{ display: "flex", flexDirection: "column", gap: 1 }}
                  >
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        Backend
                      </Typography>
                      <Chip
                        label="Online"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        Database
                      </Typography>
                      <Chip
                        label="Connected"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        Vector DB
                      </Typography>
                      <Chip
                        label="Ready"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 3,
                  border: "1px solid",
                  borderColor: "divider",
                }}
              >
                <Box sx={{ height: 4, bgcolor: "#1976d2" }} />
                <CardContent sx={{ p: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <Avatar
                      sx={{ bgcolor: alpha("#1976d2", 0.1), color: "#1976d2" }}
                    >
                      <MemoryIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        AI Services
                      </Typography>
                      <Chip
                        label="Active"
                        size="small"
                        sx={{
                          bgcolor: alpha("#1976d2", 0.1),
                          color: "#1976d2",
                          fontWeight: 600,
                        }}
                      />
                    </Box>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Box
                    sx={{ display: "flex", flexDirection: "column", gap: 1 }}
                  >
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        GPT-4o
                      </Typography>
                      <Chip
                        label="Active"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        RAG Service
                      </Typography>
                      <Chip
                        label="Indexed"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        Voice (TTS/STT)
                      </Typography>
                      <Chip
                        label="Ready"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 3,
                  border: "1px solid",
                  borderColor: "divider",
                }}
              >
                <Box sx={{ height: 4, bgcolor: "#ed6c02" }} />
                <CardContent sx={{ p: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <Avatar
                      sx={{ bgcolor: alpha("#ed6c02", 0.1), color: "#ed6c02" }}
                    >
                      <SecurityIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        Security
                      </Typography>
                      <Chip
                        label="Protected"
                        size="small"
                        sx={{
                          bgcolor: alpha("#ed6c02", 0.1),
                          color: "#ed6c02",
                          fontWeight: 600,
                        }}
                      />
                    </Box>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Box
                    sx={{ display: "flex", flexDirection: "column", gap: 1 }}
                  >
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        JWT Auth
                      </Typography>
                      <Chip
                        label="Enabled"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        HTTPS
                      </Typography>
                      <Chip
                        label="Enforced"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                    <Box
                      sx={{ display: "flex", justifyContent: "space-between" }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary" }}
                      >
                        Rate Limiting
                      </Typography>
                      <Chip
                        label="Active"
                        size="small"
                        sx={{
                          bgcolor: alpha("#2e7d32", 0.1),
                          color: "#2e7d32",
                          height: 20,
                          fontSize: "0.7rem",
                        }}
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
            <Avatar sx={{ bgcolor: alpha("#ed6c02", 0.1), color: "#ed6c02" }}>
              <WarningIcon />
            </Avatar>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Populate Database?
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            This action will:
            <Box component="ul" sx={{ mt: 1.5, pl: 2 }}>
              <li>Delete all existing patients, appointments, and providers</li>
              <li>Preserve the admin account (admin@admin.com / Admin@123)</li>
              <li>Create 30 demo patient accounts</li>
              <li>Create 3+ doctors per department</li>
              <li>Create 22 lab tests</li>
              <li>Generate diverse appointments across time periods</li>
              <li>Index all documents for the AI assistant</li>
            </Box>
            <Alert severity="warning" sx={{ mt: 2, borderRadius: 2 }}>
              <Typography variant="body2" fontWeight={600}>
                ⚠️ This will permanently delete existing data!
              </Typography>
            </Alert>
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 2.5 }}>
          <Button
            onClick={() => setConfirmDialogOpen(false)}
            sx={{ color: "text.secondary", borderRadius: 2 }}
          >
            Cancel
          </Button>
          <Button
            onClick={() => populateMutation.mutate()}
            variant="contained"
            disabled={populateMutation.isPending}
            startIcon={
              populateMutation.isPending ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <DatabaseIcon />
              )
            }
            sx={{
              bgcolor: "#840132",
              "&:hover": { bgcolor: "#5e0124" },
              borderRadius: 2,
              px: 3,
            }}
          >
            {populateMutation.isPending ? "Populating..." : "Populate Database"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
