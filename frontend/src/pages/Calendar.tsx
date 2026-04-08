import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Box,
  Typography,
  Paper,
  Grid,
  IconButton,
  Chip,
  Avatar,
  alpha,
  Dialog,
  DialogTitle,
  DialogContent,
  Fade,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Today as TodayIcon,
  AccessTime as TimeIcon,
  MedicalServices as MedicalIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  Event as EventIcon,
} from "@mui/icons-material";
import {
  format,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addDays,
  addMonths,
  subMonths,
  isSameMonth,
  isToday,
  parseISO,
} from "date-fns";
import { api } from "@/lib/api";

// Status configuration
const statusConfig: {
  [key: string]: {
    color: string;
    bgColor: string;
    icon: React.ReactElement;
    label: string;
  };
} = {
  confirmed: {
    color: "#2e7d32",
    bgColor: "#e8f5e9",
    icon: <CheckIcon fontSize="small" />,
    label: "Confirmed",
  },
  cancelled: {
    color: "#d32f2f",
    bgColor: "#ffebee",
    icon: <CancelIcon fontSize="small" />,
    label: "Cancelled",
  },
  completed: {
    color: "#1976d2",
    bgColor: "#e3f2fd",
    icon: <CheckIcon fontSize="small" />,
    label: "Completed",
  },
  no_show: {
    color: "#757575",
    bgColor: "#f5f5f5",
    icon: <CancelIcon fontSize="small" />,
    label: "No Show",
  },
};

// Helper function to format time in user's local timezone
const formatLocalTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
};

// Appointment Detail Dialog
function AppointmentDetailDialog({
  open,
  onClose,
  appointments,
  selectedDate,
  isAdmin,
}: {
  open: boolean;
  onClose: () => void;
  appointments: any[];
  selectedDate: Date | null;
  isAdmin: boolean;
}) {
  if (!selectedDate) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: 3 } }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Avatar sx={{ bgcolor: alpha("#840132", 0.1), color: "#840132" }}>
            <EventIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {format(selectedDate, "EEEE, MMMM d, yyyy")}
            </Typography>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              {appointments.length} appointment
              {appointments.length !== 1 ? "s" : ""}
            </Typography>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent>
        {appointments.length === 0 ? (
          <Box sx={{ textAlign: "center", py: 4 }}>
            <EventIcon sx={{ fontSize: 48, color: "text.disabled", mb: 2 }} />
            <Typography variant="body1" sx={{ color: "text.secondary" }}>
              No appointments on this day
            </Typography>
          </Box>
        ) : (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            {appointments.map((appt: any, index: number) => {
              const status =
                statusConfig[appt.status] || statusConfig.confirmed;
              return (
                <Fade in key={appt.id} timeout={300 + index * 100}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2.5,
                      borderRadius: 2,
                      border: "1px solid",
                      borderColor: "divider",
                      borderLeft: `4px solid ${status.color}`,
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        mb: 1.5,
                      }}
                    >
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1.5 }}
                      >
                        <Avatar
                          sx={{
                            width: 40,
                            height: 40,
                            bgcolor: alpha("#840132", 0.1),
                            color: "#840132",
                          }}
                        >
                          <MedicalIcon fontSize="small" />
                        </Avatar>
                        <Box>
                          <Typography
                            variant="subtitle1"
                            sx={{ fontWeight: 700 }}
                          >
                            {appt.provider_name}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{ color: "text.secondary" }}
                          >
                            {appt.provider_department}
                          </Typography>
                          {isAdmin && appt.user_name && (
                            <Typography
                              variant="body2"
                              sx={{
                                color: "#840132",
                                fontWeight: 600,
                                mt: 0.5,
                              }}
                            >
                              Patient: {appt.user_name}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                      <Chip
                        icon={status.icon}
                        label={status.label}
                        size="small"
                        sx={{
                          bgcolor: status.bgColor,
                          color: status.color,
                          fontWeight: 600,
                          "& .MuiChip-icon": { color: status.color },
                        }}
                      />
                    </Box>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 3,
                        mt: 2,
                      }}
                    >
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <TimeIcon
                          sx={{ fontSize: 18, color: "text.secondary" }}
                        />
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {formatLocalTime(appt.time_start)}
                        </Typography>
                      </Box>
                      {appt.reason && (
                        <Typography
                          variant="body2"
                          sx={{ color: "text.secondary" }}
                        >
                          {appt.reason}
                        </Typography>
                      )}
                    </Box>
                    {appt.confirmation_code && (
                      <Chip
                        label={`Code: ${appt.confirmation_code}`}
                        size="small"
                        variant="outlined"
                        sx={{ mt: 1.5, fontFamily: "monospace" }}
                      />
                    )}
                  </Paper>
                </Fade>
              );
            })}
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default function CalendarPage() {
  const currentUser = api.getCurrentUser();
  const isAdmin =
    currentUser?.role === "admin" || currentUser?.role === "staff";

  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Fetch appointments
  const { data: appointments, isLoading } = useQuery({
    queryKey: ["appointments", isAdmin],
    queryFn: () =>
      isAdmin
        ? api.getAppointments()
        : api.getAppointments({ user_id: currentUser?.id }),
  });

  // Group appointments by date
  const appointmentsByDate = useMemo(() => {
    const grouped: { [key: string]: any[] } = {};
    appointments?.forEach((appt: any) => {
      const dateKey = format(parseISO(appt.time_start), "yyyy-MM-dd");
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(appt);
    });
    return grouped;
  }, [appointments]);

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart);
    const endDate = endOfWeek(monthEnd);

    const days = [];
    let day = startDate;

    while (day <= endDate) {
      days.push(day);
      day = addDays(day, 1);
    }

    return days;
  }, [currentMonth]);

  const handlePrevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));
  const handleNextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));
  const handleToday = () => setCurrentMonth(new Date());

  const handleDateClick = (date: Date) => {
    setSelectedDate(date);
    setDialogOpen(true);
  };

  const getAppointmentsForDate = (date: Date) => {
    const dateKey = format(date, "yyyy-MM-dd");
    return appointmentsByDate[dateKey] || [];
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 400,
        }}
      >
        <CircularProgress sx={{ color: "#840132" }} />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto" }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 800,
            background: "linear-gradient(135deg, #840132 0%, #5e0124 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            mb: 1,
          }}
        >
          Appointment Calendar
        </Typography>
        <Typography variant="body1" sx={{ color: "text.secondary" }}>
          View your scheduled appointments at a glance
        </Typography>
      </Box>

      {/* Calendar Card */}
      <Paper
        elevation={0}
        sx={{
          borderRadius: 2,
          border: "1px solid",
          borderColor: "divider",
          overflow: "hidden",
        }}
      >
        {/* Calendar Header */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            px: 3,
            py: 2.5,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "#fafbfc",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <IconButton
              onClick={handlePrevMonth}
              size="small"
              sx={{
                color: "text.secondary",
                border: "1px solid",
                borderColor: "divider",
                "&:hover": {
                  bgcolor: alpha("#840132", 0.05),
                  borderColor: "#840132",
                  color: "#840132",
                },
              }}
            >
              <ChevronLeftIcon fontSize="small" />
            </IconButton>
            <IconButton
              onClick={handleNextMonth}
              size="small"
              sx={{
                color: "text.secondary",
                border: "1px solid",
                borderColor: "divider",
                "&:hover": {
                  bgcolor: alpha("#840132", 0.05),
                  borderColor: "#840132",
                  color: "#840132",
                },
              }}
            >
              <ChevronRightIcon fontSize="small" />
            </IconButton>
          </Box>

          <Box sx={{ display: "flex", alignItems: "baseline", gap: 1.5 }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 700,
                color: "#840132",
              }}
            >
              {format(currentMonth, "MMMM")}
            </Typography>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 400,
                color: "text.secondary",
              }}
            >
              {format(currentMonth, "yyyy")}
            </Typography>
          </Box>

          <Tooltip title="Go to today">
            <IconButton
              onClick={handleToday}
              size="small"
              sx={{
                color: "text.secondary",
                border: "1px solid",
                borderColor: "divider",
                "&:hover": {
                  bgcolor: alpha("#840132", 0.05),
                  borderColor: "#840132",
                  color: "#840132",
                },
              }}
            >
              <TodayIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Day Headers */}
        <Grid
          container
          sx={{
            bgcolor: "#f8f9fa",
            borderBottom: "1px solid",
            borderColor: "divider",
          }}
        >
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
            <Grid item xs={12 / 7} key={day}>
              <Box sx={{ py: 1.5, textAlign: "center" }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 700,
                    color: "text.secondary",
                    textTransform: "uppercase",
                    fontSize: "0.75rem",
                  }}
                >
                  {day}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Calendar Grid */}
        <Grid container>
          {calendarDays.map((day, index) => {
            const dayAppointments = getAppointmentsForDate(day);
            const hasAppointments = dayAppointments.length > 0;
            const isCurrentMonth = isSameMonth(day, currentMonth);
            const isCurrentDay = isToday(day);

            return (
              <Grid
                item
                xs={12 / 7}
                key={index}
                sx={{
                  borderBottom: "1px solid",
                  borderRight: (index + 1) % 7 !== 0 ? "1px solid" : "none",
                  borderColor: "divider",
                }}
              >
                <Box
                  onClick={() => handleDateClick(day)}
                  sx={{
                    minHeight: 100,
                    p: 1,
                    cursor: "pointer",
                    bgcolor: isCurrentDay
                      ? alpha("#840132", 0.05)
                      : "transparent",
                    opacity: isCurrentMonth ? 1 : 0.4,
                    transition: "all 0.2s ease",
                    "&:hover": {
                      bgcolor: alpha("#840132", 0.08),
                    },
                  }}
                >
                  {/* Day Number */}
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "flex-end",
                      mb: 0.5,
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 28,
                        height: 28,
                        fontSize: "0.875rem",
                        fontWeight: isCurrentDay ? 700 : 500,
                        bgcolor: isCurrentDay ? "#840132" : "transparent",
                        color: isCurrentDay ? "white" : "text.primary",
                      }}
                    >
                      {format(day, "d")}
                    </Avatar>
                  </Box>

                  {/* Appointment Indicators */}
                  {hasAppointments && (
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 0.5,
                      }}
                    >
                      {dayAppointments.slice(0, 2).map((appt: any) => {
                        const status =
                          statusConfig[appt.status] || statusConfig.confirmed;
                        return (
                          <Box
                            key={appt.id}
                            sx={{
                              px: 1,
                              py: 0.5,
                              borderRadius: 1,
                              bgcolor: status.bgColor,
                              borderLeft: `3px solid ${status.color}`,
                            }}
                          >
                            <Typography
                              variant="caption"
                              sx={{
                                fontWeight: 600,
                                color: status.color,
                                display: "block",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                                fontSize: "0.7rem",
                              }}
                            >
                              {formatLocalTime(appt.time_start)}
                            </Typography>
                            <Typography
                              variant="caption"
                              sx={{
                                color: "text.secondary",
                                display: "block",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                                fontSize: "0.65rem",
                              }}
                            >
                              {appt.provider_name
                                ?.split(" ")
                                .slice(0, 2)
                                .join(" ")}
                            </Typography>
                          </Box>
                        );
                      })}
                      {dayAppointments.length > 2 && (
                        <Typography
                          variant="caption"
                          sx={{
                            color: "#840132",
                            fontWeight: 600,
                            pl: 1,
                            fontSize: "0.7rem",
                          }}
                        >
                          +{dayAppointments.length - 2} more
                        </Typography>
                      )}
                    </Box>
                  )}
                </Box>
              </Grid>
            );
          })}
        </Grid>

        {/* Legend */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 3,
            p: 2,
            borderTop: "1px solid",
            borderColor: "divider",
            bgcolor: "#f8f9fa",
          }}
        >
          {Object.entries(statusConfig)
            .slice(0, 4)
            .map(([key, value]) => (
              <Box
                key={key}
                sx={{ display: "flex", alignItems: "center", gap: 1 }}
              >
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    bgcolor: value.color,
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{ color: "text.secondary", fontWeight: 500 }}
                >
                  {value.label}
                </Typography>
              </Box>
            ))}
        </Box>
      </Paper>

      {/* Summary Stats */}
      <Grid container spacing={2} sx={{ mt: 3 }}>
        {[
          {
            label: "Total Appointments",
            value: appointments?.length || 0,
            color: "#840132",
          },
          {
            label: "Confirmed",
            value:
              appointments?.filter((a: any) => a.status === "confirmed")
                .length || 0,
            color: "#2e7d32",
          },
          {
            label: "Completed",
            value:
              appointments?.filter((a: any) => a.status === "completed")
                .length || 0,
            color: "#ed6c02",
          },
          {
            label: "This Month",
            value:
              appointments?.filter((a: any) =>
                isSameMonth(parseISO(a.time_start), currentMonth),
              ).length || 0,
            color: "#1976d2",
          },
        ].map((stat) => (
          <Grid item xs={6} md={3} key={stat.label}>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                borderRadius: 2,
                border: "1px solid",
                borderColor: "divider",
                display: "flex",
                alignItems: "center",
                gap: 2,
                bgcolor: "#fff",
              }}
            >
              <Box
                sx={{
                  width: 44,
                  height: 44,
                  borderRadius: 1.5,
                  bgcolor: alpha(stat.color, 0.08),
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 700, color: stat.color }}
                >
                  {stat.value}
                </Typography>
              </Box>
              <Typography
                variant="body2"
                sx={{ color: "text.secondary", fontWeight: 500 }}
              >
                {stat.label}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Appointment Detail Dialog */}
      <AppointmentDetailDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        appointments={selectedDate ? getAppointmentsForDate(selectedDate) : []}
        selectedDate={selectedDate}
        isAdmin={isAdmin}
      />
    </Box>
  );
}
