import React, { createContext, useContext, useState, useEffect } from 'react';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Verificar se há token salvo ao carregar a aplicação
  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Erro ao carregar usuário:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }

    setLoading(false);
  }, []);

  const login = async (credentials) => {
    try {
      setLoading(true);

      console.log('🔄 Tentando fazer login...', credentials);

      // Fazer requisição para o backend
      const response = await fetch('http://127.0.0.1:8001/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      console.log('📡 Resposta da API:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Erro de conexão' }));
        throw new Error(errorData.detail || `Erro ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Login bem-sucedido:', data);

      const { access_token, user: userData } = data;

      // Salvar token e dados do usuário
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      setUser(userData);

      toast.success(`Bem-vindo, ${userData.full_name}! 🎉`);

      return { success: true, user: userData };
    } catch (error) {
      console.error('❌ Erro no login:', error);

      // Verificar se é erro de conexão
      if (error.message.includes('fetch')) {
        toast.error('❌ Erro de conexão! Verifique se o backend está rodando na porta 8001');
      } else {
        toast.error(`❌ ${error.message}`);
      }

      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        // Tentar fazer logout no backend
        await fetch('http://127.0.0.1:8001/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }).catch(() => {
          // Ignorar erro de logout se backend não responder
          console.log('Backend não respondeu ao logout, mas continuando...');
        });
      }
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    } finally {
      // Limpar dados locais
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      toast.success('Logout realizado com sucesso');
    }
  };

  const isAdmin = () => {
    return user?.access_level === 'master';
  };

  const isCoordinator = () => {
    return user?.access_level === 'coordenador' || user?.access_level === 'master';
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAdmin,
    isCoordinator,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};