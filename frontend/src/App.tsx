import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import ChatPage from './pages/Chat';
import AppointmentsPage from './pages/Appointments';
import LabsPage from './pages/Labs';
import AdminPage from './pages/Admin';
import IncidentsPage from './pages/Incidents';
import ProvidersPage from './pages/Providers';
import LoginPage from './pages/Login';

function App() {
  const isAuthenticated = Boolean(localStorage.getItem('access_token'));

  return (
    <BrowserRouter>
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Layout>
                  <ChatPage />
                </Layout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/chat"
            element={
              isAuthenticated ? (
                <Layout>
                  <ChatPage />
                </Layout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/appointments"
            element={
              isAuthenticated ? (
                <Layout>
                  <AppointmentsPage />
                </Layout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/labs"
            element={
              isAuthenticated ? (
                <Layout>
                  <LabsPage />
                </Layout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/providers"
            element={
              isAuthenticated ? (
                <Layout>
                  <ProvidersPage />
                </Layout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/admin"
            element={
              isAuthenticated ? (
                <Layout>
                  <AdminPage />
                </Layout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/incidents"
            element={
              isAuthenticated ? (
                <Layout>
                  <IncidentsPage />
                </Layout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
        </Routes>
      </Box>
    </BrowserRouter>
  );
}

export default App;
