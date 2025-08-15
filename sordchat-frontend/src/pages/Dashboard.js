import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocket } from '../contexts/WebSocketContext';
//import { dashboardService, healthService } from '../services/api';
import Loading from '../components/common/Loading';

const Dashboard = () => {
  const { user } = useAuth();
  const { connected, onlineUsers } = useWebSocket();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);

  // Carregar dados do dashboard
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);

        // Simular dados se a API não responder
        setTimeout(() => {
          setDashboardData({
            stats: {
              tickets: { total: 4, abertos: 3, created_today: 2 },
              tasks: { total: 4, concluidas: 1, em_progresso: 1 },
              messages: { total: 25, unread: 1, today: 8 },
              users: { total: 3, online: onlineUsers.length + 1, active: 3 }
            },
            recent_activity: [
              {
                icon: '📋',
                description: 'Nova task criada: Desenvolver interface do usuário',
                user: 'João Silva',
                timestamp: new Date().toISOString()
              },
              {
                icon: '💬',
                description: 'Nova mensagem no chat geral',
                user: 'Administrador Master',
                timestamp: new Date().toISOString()
              }
            ]
          });

          setSystemInfo({
            version: '1.0.0',
            statistics: {
              websocket_connections: 1,
              uploaded_files: 0
            }
          });

          setLoading(false);
        }, 1000);

      } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [onlineUsers.length]);

  if (loading) {
    return <Loading text="Carregando dashboard..." />;
  }

  const stats = dashboardData?.stats || {};
  const recentActivity = dashboardData?.recent_activity || [];

  return (
    <div className="space-y-6">
      {/* Boas-vindas */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Bem-vindo, {user?.full_name}! 👋
            </h1>
            <p className="text-blue-100">
              {new Date().toLocaleDateString('pt-BR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2 mb-2">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm">
                {connected ? 'Online' : 'Desconectado'}
              </span>
            </div>
            <p className="text-sm text-blue-100">
              {onlineUsers.length + 1} usuários online
            </p>
          </div>
        </div>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Tickets */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tickets</p>
              <p className="text-2xl font-bold text-gray-900">{stats.tickets?.total || 0}</p>
              <p className="text-sm text-gray-500">
                {stats.tickets?.abertos || 0} abertos
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🎫</span>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-600">↗</span>
            <span className="text-green-600 ml-1">+{stats.tickets?.created_today || 0}</span>
            <span className="text-gray-500 ml-1">hoje</span>
          </div>
        </div>

        {/* Tasks */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{stats.tasks?.total || 0}</p>
              <p className="text-sm text-gray-500">
                {stats.tasks?.concluidas || 0} concluídas
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📋</span>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-blue-600">→</span>
            <span className="text-blue-600 ml-1">{stats.tasks?.em_progresso || 0}</span>
            <span className="text-gray-500 ml-1">em progresso</span>
          </div>
        </div>

        {/* Mensagens */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Mensagens</p>
              <p className="text-2xl font-bold text-gray-900">{stats.messages?.total || 0}</p>
              <p className="text-sm text-gray-500">
                {stats.messages?.unread || 0} não lidas
              </p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💬</span>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-purple-600">↗</span>
            <span className="text-purple-600 ml-1">+{stats.messages?.today || 0}</span>
            <span className="text-gray-500 ml-1">hoje</span>
          </div>
        </div>

        {/* Usuários */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Usuários</p>
              <p className="text-2xl font-bold text-gray-900">{stats.users?.total || 0}</p>
              <p className="text-sm text-gray-500">
                {stats.users?.online || 0} online
              </p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">👥</span>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-600">●</span>
            <span className="text-green-600 ml-1">{stats.users?.active || 0}</span>
            <span className="text-gray-500 ml-1">ativos</span>
          </div>
        </div>
      </div>

      {/* Atividade recente e Status do sistema */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Atividade recente */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Atividade Recente</h3>
          <div className="space-y-4">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm">{activity.icon}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.description}</p>
                    <p className="text-xs text-gray-500">
                      {activity.user} • {new Date(activity.timestamp).toLocaleString('pt-BR')}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">Nenhuma atividade recente</p>
            )}
          </div>
        </div>

        {/* Status do sistema */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Status do Sistema</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Status</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                ✅ Online
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">WebSocket</span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {connected ? '✅ Conectado' : '❌ Desconectado'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Versão</span>
              <span className="text-sm text-gray-900">{systemInfo?.version || '1.0.0'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Ações rápidas */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Ações Rápidas</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex flex-col items-center p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
            <span className="text-2xl mb-2">🎫</span>
            <span className="text-sm font-medium text-blue-700">Novo Ticket</span>
          </button>

          <button className="flex flex-col items-center p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors">
            <span className="text-2xl mb-2">📋</span>
            <span className="text-sm font-medium text-green-700">Nova Task</span>
          </button>

          <button className="flex flex-col items-center p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors">
            <span className="text-2xl mb-2">💬</span>
            <span className="text-sm font-medium text-purple-700">Abrir Chat</span>
          </button>

          <button className="flex flex-col items-center p-4 bg-yellow-50 hover:bg-yellow-100 rounded-lg transition-colors">
            <span className="text-2xl mb-2">📁</span>
            <span className="text-sm font-medium text-yellow-700">Upload Arquivo</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;