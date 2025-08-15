import React from 'react';
import './index.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg text-center">
        <h1 className="text-3xl font-bold text-blue-600 mb-4">
          🚀 SorDChat Frontend
        </h1>
        <p className="text-gray-600 mb-4">
          Sistema funcionando!
        </p>
        <div className="space-y-2">
          <p className="text-sm text-green-600">✅ React carregado</p>
          <p className="text-sm text-green-600">✅ Tailwind CSS funcionando</p>
          <p className="text-sm text-blue-600">🔄 Pronto para desenvolvimento</p>
        </div>
      </div>
    </div>
  );
}

export default App;