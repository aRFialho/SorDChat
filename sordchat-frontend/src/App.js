import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Loading from './components/common/Loading';
import Toast from './components/common/Toast';
import Chat from './pages/Chat';
import Kanban from './pages/Kanban';
<Route path="/kanban" element={<Kanban />} />
// Componente para proteger rotas
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <Loading fullScreen text="Verificando autenticação..." />;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Componente para redirecionar usuários autenticados
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <Loading fullScreen text="Verificando autenticação..." />;
  }

  return !isAuthenticated ? children : <Navigate to="/dashboard" />;
};

// Páginas temporárias para desenvolvimento
const ComingSoon = ({ title }) => (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <div className="text-6xl mb-4">🚧</div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">{title}</h2>
      <p className="text-gray-600">Esta página está em desenvolvimento</p>
    </div>
  </div>
);

// Componente principal das rotas protegidas
const ProtectedApp = () => {
  return (
    <WebSocketProvider>
      <Layout>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tickets" element={<ComingSoon title="Tickets" />} />
          <Route path="/tasks" element={<ComingSoon title="Tasks" />} />
          <Route path="/files" element={<ComingSoon title="Arquivos" />} />
          <Route path="/users" element={<ComingSoon title="Usuários" />} />
          <Route path="/notifications" element={<ComingSoon title="Notificações" />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </WebSocketProvider>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toast />
          <Routes>
            {/* Rota pública - Login */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              }
            />

            {/* Rotas protegidas */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <ProtectedApp />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;