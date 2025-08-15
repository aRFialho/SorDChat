import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Login = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!credentials.username || !credentials.password) {
      toast.error('Por favor, preencha todos os campos');
      return;
    }

    setLoading(true);

    try {
      const result = await login(credentials);

      if (result.success) {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Erro no login:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  // Credenciais de demonstração
  const demoCredentials = [
    { username: 'admin', password: 'admin123', role: 'Administrador Master' },
    { username: 'coordenador', password: 'coord123', role: 'Coordenador' },
    { username: 'usuario', password: 'user123', role: 'Usuário Padrão' }
  ];

  const fillDemo = (demo) => {
    setCredentials({
      username: demo.username,
      password: demo.password
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo e título */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white bg-opacity-20 rounded-full mb-4">
            <span className="text-2xl">💬</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">SorDChat</h1>
          <p className="text-blue-100">Sistema Corporativo de Comunicação</p>
        </div>

        {/* Card de login */}
        <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white border-opacity-20">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-white mb-2">
                Usuário
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={credentials.username}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-white placeholder-blue-100 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
                placeholder="Digite seu usuário"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-white mb-2">
                Senha
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={credentials.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-white placeholder-blue-100 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
                placeholder="Digite sua senha"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 border border-white border-opacity-30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="spinner mr-2"></div>
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </button>
          </form>

          {/* Credenciais de demonstração */}
          <div className="mt-8 pt-6 border-t border-white border-opacity-20">
            <p className="text-sm text-blue-100 mb-4 text-center">Credenciais de demonstração:</p>
            <div className="space-y-2">
              {demoCredentials.map((demo, index) => (
                <button
                  key={index}
                  onClick={() => fillDemo(demo)}
                  className="w-full text-left p-3 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition-all duration-200 border border-white border-opacity-20"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-white font-medium">{demo.username}</p>
                      <p className="text-blue-100 text-sm">{demo.role}</p>
                    </div>
                    <span className="text-blue-100 text-sm">Clique para usar</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;