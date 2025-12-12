import React from 'react';
import { MemoryRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { DashboardHome } from './components/dashboard/DashboardHome';
import { AnalysisPage } from './pages/AnalysisPage';
import { StrategiesPage } from './pages/StrategiesPage';
import { SignalsPage } from './pages/SignalsPage';
import { BacktestPage } from './pages/BacktestPage';
import { LogsPage } from './pages/LogsPage';
import { SettingsPage } from './pages/SettingsPage';
import { LoginPage } from './pages/LoginPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastContainer } from './components/Toast';
import { Loader2 } from 'lucide-react';
import DevPanel from "./components/DevPanel";
import { AdvisorChat } from './components/AdvisorChat';

// Wrapper for Protected Routes
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#020617] text-indigo-500">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <MainLayout>{children}</MainLayout>;
};

const App: React.FC = () => {
  const [chatOpen, setChatOpen] = React.useState(false);
  const [chatContext, setChatContext] = React.useState<{ token?: string, context?: any }>({});

  React.useEffect(() => {
    const handleOpenChat = (e: any) => {
      setChatContext(e.detail || {});
      setChatOpen(true);
    };

    window.addEventListener('open-advisor-chat', handleOpenChat);
    return () => window.removeEventListener('open-advisor-chat', handleOpenChat);
  }, []);

  return (
    <AuthProvider>
      <Router>
        <ToastContainer />
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <>
                  <DashboardHome />
                  <DevPanel />
                </>
              </ProtectedRoute>
            }
          />
          <Route path="/analysis" element={<ProtectedRoute><AnalysisPage /></ProtectedRoute>} />
          <Route path="/strategies" element={<ProtectedRoute><StrategiesPage /></ProtectedRoute>} />
          <Route path="/signals" element={<ProtectedRoute><SignalsPage /></ProtectedRoute>} />
          <Route path="/logs" element={<ProtectedRoute><LogsPage /></ProtectedRoute>} />
          <Route path="/backtest" element={<ProtectedRoute><BacktestPage /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Global Advisor Chat Overlay */}
        {chatOpen && (
          <div className="fixed bottom-0 right-0 z-[60] h-[600px] w-full md:w-auto shadow-2xl animate-in slide-in-from-right-10 duration-300">
            <AdvisorChat
              token={chatContext.token}
              context={chatContext.context}
              onClose={() => setChatOpen(false)}
            />
          </div>
        )}

      </Router>
    </AuthProvider>
  );
};

export default App;
