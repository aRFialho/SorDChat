import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocket } from '../../contexts/WebSocketContext';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user, logout, isCoordinator } = useAuth();
  const { connected, onlineUsers } = useWebSocket();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Menu items baseado nas permissões
  const menuItems = [
    {
      name: 'Dashboard',
      icon: '📊',
      path: '/dashboard',
      show: true
    },
    {
      name: 'Chat',
      icon: '💬',
      path: '/chat',
      show: true,
      badge: connected ? '🟢' : '🔴'
    },
    {
      name: 'Tickets',
      icon: '🎫',
      path: '/tickets',
      show: true
    },
    {
      name: 'Tasks',
      icon: '📋',
      path: '/tasks',
      show: true
    },
    {
      name: 'Arquivos',
      icon: '📁',
      path: '/files',
      show: true
    },
    {
      name: 'Usuários',
      icon: '👥',
      path: '/users',
      show: isCoordinator()
    },
    {
      name: 'Notificações',
      icon: '🔔',
      path: '/notifications',
      show: true
    }
  ];

  const visibleMenuItems = menuItems.filter(item => item.show);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white shadow-lg transition-all duration-300 flex flex-col`}>
        {/* Header da sidebar */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <div className="flex items-center space-x-2">
                <span className="text-2xl">💬</span>
                <h1 className="text-xl font-bold text-gray-800">SorDChat</h1>
              </div>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {sidebarOpen ? '◀' : '▶'}
            </button>
          </div>
        </div>

        {/* Status de conexão */}
        {sidebarOpen && (
          <div className="px-4 py-2 border-b border-gray-200">
            <div className="flex items-center space-x-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-gray-600">
                {connected ? 'Online' : 'Desconectado'}
              </span>
              {connected && (
                <span className="text-gray-500">
                  ({onlineUsers.length} usuários online)
                </span>
              )}
            </div>
          </div>
        )}

        {/* Menu de navegação */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {visibleMenuItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <button
                    onClick={() => navigate(item.path)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-100 text-blue-700 border border-blue-200'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    {sidebarOpen && (
                      <>
                        <span className="font-medium">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto text-xs">{item.badge}</span>
                        )}
                      </>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Perfil do usuário */}
        <div className="p-4 border-t border-gray-200">
          {sidebarOpen ? (
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 font-semibold">
                    {user?.full_name?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {user?.full_name}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user?.access_level === 'master' ? 'Administrador' :
                     user?.access_level === 'coordenador' ? 'Coordenador' : 'Usuário'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <span>🚪</span>
                <span>Sair</span>
              </button>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Sair"
            >
              🚪
            </button>
          )}
        </div>
      </div>

      {/* Conteúdo principal */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-gray-800">
                {getPageTitle(location.pathname)}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {getPageDescription(location.pathname)}
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/notifications')}
                className="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="text-xl">🔔</span>
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
              </button>

              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>{user?.username}</span>
              </div>
            </div>
          </div>
        </header>

        {/* Conteúdo da página */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

// Função para obter título da página
const getPageTitle = (pathname) => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/chat': 'Chat',
    '/tickets': 'Tickets',
    '/tasks': 'Tasks',
    '/files': 'Arquivos',
    '/users': 'Usuários',
    '/notifications': 'Notificações'
  };
  return titles[pathname] || 'SorDChat';
};

// Função para obter descrição da página
const getPageDescription = (pathname) => {
  const descriptions = {
    '/dashboard': 'Visão geral do sistema e estatísticas',
    '/chat': 'Comunicação em tempo real',
    '/tickets': 'Gerenciamento de tickets de suporte',
    '/tasks': 'Controle de tarefas e projetos',
    '/files': 'Upload e gerenciamento de arquivos',
    '/users': 'Gerenciamento de usuários do sistema',
    '/notifications': 'Central de notificações'
  };
  return descriptions[pathname] || 'Sistema corporativo de comunicação';
};

export default Layout;