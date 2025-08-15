import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocket } from '../contexts/WebSocketContext';
import toast from 'react-hot-toast';

const Chat = () => {
  const { user } = useAuth();
  const {
    connected,
    onlineUsers,
    messages,
    typingUsers,
    unreadCount,
    sendMessage,
    sendTypingIndicator,
    markAsRead,
    uploadFile,
    sendReaction
  } = useWebSocket();

  const [newMessage, setNewMessage] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [showReactionPicker, setShowReactionPicker] = useState(null);

  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const fileInputRef = useRef(null);

  // Emojis populares
  const popularEmojis = ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕'];

  // Emojis para reações rápidas
  const quickReactions = ['👍', '❤️', '😂', '😮', '😢', '😡'];

  // Auto-scroll para a última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Marcar como lidas quando abrir o chat
  useEffect(() => {
    markAsRead();
  }, [markAsRead]);

  // Filtrar mensagens baseado no usuário selecionado
  const filteredMessages = selectedUser
    ? messages.filter(msg =>
        (msg.sender_id === selectedUser.id && msg.receiver_id === user?.id) ||
        (msg.sender_id === user?.id && msg.receiver_id === selectedUser.id)
      )
    : messages.filter(msg => !msg.receiver_id); // Mensagens do chat geral

  // Filtrar mensagens por busca
  const searchFilteredMessages = searchTerm
    ? filteredMessages.filter(msg =>
        msg.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        msg.sender_name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : filteredMessages;

  // Enviar mensagem
  const handleSendMessage = (e) => {
    e.preventDefault();

    if (!newMessage.trim()) return;

    sendMessage(newMessage.trim(), selectedUser?.id);
    setNewMessage('');
    setShowEmojiPicker(false);

    // Parar indicador de digitação
    if (isTyping) {
      sendTypingIndicator(false, selectedUser?.id);
      setIsTyping(false);
    }
  };

  // Indicador de digitação
  const handleTyping = (e) => {
    setNewMessage(e.target.value);

    if (!isTyping) {
      setIsTyping(true);
      sendTypingIndicator(true, selectedUser?.id);
    }

    // Limpar timeout anterior
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Parar indicador após 2 segundos sem digitar
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      sendTypingIndicator(false, selectedUser?.id);
    }, 2000);
  };

  // Adicionar emoji
  const addEmoji = (emoji) => {
    setNewMessage(prev => prev + emoji);
    setShowEmojiPicker(false);
  };

  // Upload de arquivo
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);

    try {
      const uploadResult = await uploadFile(file);

      // Enviar mensagem com arquivo
      const fileMessage = `📁 ${file.name}`;
      sendMessage(fileMessage, selectedUser?.id, 'file', uploadResult.file_path);

      toast.success('Arquivo enviado com sucesso! 📁');
    } catch (error) {
      toast.error('Erro ao enviar arquivo');
    } finally {
      setIsUploading(false);
      // Limpar input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Função para reagir à mensagem
  const handleReaction = async (messageId, emoji) => {
    try {
      await sendReaction(messageId, emoji);
      setShowReactionPicker(null);
    } catch (error) {
      // Erro já tratado no context
    }
  };

  // Formatar timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } else {
      return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  // Verificar se usuário está digitando
  const getUserTyping = () => {
    if (selectedUser) {
      return typingUsers.find(u => u.id === selectedUser.id);
    }
    return typingUsers.find(u => u.id !== user?.id);
  };

  const userTyping = getUserTyping();

  // Renderizar mensagem com reações
  const renderMessage = (message) => {
    const isOwnMessage = message.sender_id === user?.id;
    const isFileMessage = message.message_type === 'file';
    const reactions = message.reactions || [];

    return (
      <div
        key={message.id}
        className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4 group`}
      >
        <div className="max-w-xs lg:max-w-md">
          {/* Mensagem */}
          <div
            className={`px-4 py-3 rounded-lg relative ${
              isOwnMessage
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {!isOwnMessage && !selectedUser && (
              <p className="text-xs font-medium mb-1 opacity-75">
                {message.sender_name}
              </p>
            )}

            {isFileMessage ? (
              <div className="flex items-center space-x-2">
                <span className="text-lg">📁</span>
                <div>
                  <p className="text-sm font-medium">{message.content.replace('📁 ', '')}</p>
                  <button
                    onClick={() => window.open(`http://127.0.0.1:8001/files/download/${message.file_path}`, '_blank')}
                    className={`text-xs underline ${isOwnMessage ? 'text-blue-100' : 'text-blue-600'}`}
                  >
                    Baixar arquivo
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            )}

            <p className={`text-xs mt-1 ${isOwnMessage ? 'text-blue-100' : 'text-gray-500'}`}>
              {formatTime(message.timestamp)}
            </p>

            {/* Botão de reação (aparece no hover) */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowReactionPicker(showReactionPicker === message.id ? null : message.id);
              }}
              className={`absolute -top-2 ${isOwnMessage ? '-left-8' : '-right-8'} 
                opacity-0 group-hover:opacity-100 transition-opacity
                w-6 h-6 bg-gray-200 hover:bg-gray-300 rounded-full 
                flex items-center justify-center text-sm z-10`}
            >
              😊
            </button>
          </div>

          {/* Picker de reações */}
          {showReactionPicker === message.id && (
            <div
              className={`mt-2 p-2 bg-white border border-gray-200 rounded-lg shadow-lg 
                flex space-x-1 z-20 ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
              onClick={(e) => e.stopPropagation()}
            >
              {quickReactions.map((emoji) => (
                <button
                  key={emoji}
                  onClick={() => handleReaction(message.id, emoji)}
                  className="text-lg hover:bg-gray-100 rounded p-1 transition-colors"
                >
                  {emoji}
                </button>
              ))}
            </div>
          )}

          {/* Reações existentes */}
          {reactions.length > 0 && (
            <div className={`mt-2 flex flex-wrap gap-1 ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
              {reactions.map((reaction) => (
                <button
                  key={reaction.emoji}
                  onClick={() => handleReaction(message.id, reaction.emoji)}
                  className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs
                    transition-colors ${
                      reaction.reacted_by_me
                        ? 'bg-blue-100 text-blue-700 border border-blue-200'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  title={`${reaction.users.join(', ')}`}
                >
                  <span>{reaction.emoji}</span>
                  <span>{reaction.count}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Fechar picker ao clicar fora
  useEffect(() => {
    const handleClickOutside = () => {
      setShowReactionPicker(null);
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <div className="flex h-full bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Sidebar - Lista de usuários */}
      <div className="w-80 border-r border-gray-200 flex flex-col">
        {/* Header da sidebar */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-800">Chat</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {connected ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>

          {/* Busca */}
          <input
            type="text"
            placeholder="Buscar mensagens..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Chat Geral */}
        <div className="p-2">
          <button
            onClick={() => setSelectedUser(null)}
            className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
              !selectedUser 
                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                : 'hover:bg-gray-100'
            }`}
          >
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold">💬</span>
            </div>
            <div className="flex-1 text-left">
              <p className="font-medium text-gray-900">Chat Geral</p>
              <p className="text-sm text-gray-500">Conversa em grupo</p>
            </div>
            {!selectedUser && unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                {unreadCount}
              </span>
            )}
          </button>
        </div>

        {/* Lista de usuários online */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            <h4 className="text-sm font-medium text-gray-500 mb-2 px-3">
              Usuários Online ({onlineUsers.length})
            </h4>
            <div className="space-y-1">
              {onlineUsers.map((onlineUser) => (
                <button
                  key={onlineUser.id}
                  onClick={() => setSelectedUser(onlineUser)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                    selectedUser?.id === onlineUser.id 
                      ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="relative">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">
                        {onlineUser.full_name?.charAt(0) || onlineUser.username?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                  </div>
                  <div className="flex-1 text-left">
                    <p className="font-medium text-gray-900">
                      {onlineUser.full_name || onlineUser.username}
                    </p>
                    <p className="text-sm text-gray-500">Online</p>
                  </div>
                  {typingUsers.find(u => u.id === onlineUser.id) && (
                    <div className="text-blue-500 text-xs">
                      digitando...
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Área principal do chat */}
      <div className="flex-1 flex flex-col">
        {/* Header do chat */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {selectedUser ? (
                <>
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-semibold">
                      {selectedUser.full_name?.charAt(0) || selectedUser.username?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">
                      {selectedUser.full_name || selectedUser.username}
                    </h3>
                    <p className="text-sm text-green-600">Online</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">💬</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">Chat Geral</h3>
                    <p className="text-sm text-gray-600">
                      {onlineUsers.length + 1} participantes online
                    </p>
                  </div>
                </>
              )}
            </div>

            {searchTerm && (
              <div className="text-sm text-gray-600">
                {searchFilteredMessages.length} mensagem(s) encontrada(s)
              </div>
            )}
          </div>
        </div>

        {/* Área de mensagens */}
        <div className="flex-1 overflow-y-auto p-4">
          {!connected && (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🔌</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Desconectado</h3>
              <p className="text-gray-600">Tentando reconectar ao chat...</p>
            </div>
          )}

          {connected && searchFilteredMessages.length === 0 && !searchTerm && (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                {selectedUser ? 'Nenhuma mensagem ainda' : 'Seja o primeiro a enviar uma mensagem!'}
              </h3>
              <p className="text-gray-600">
                {selectedUser
                  ? `Comece uma conversa com ${selectedUser.full_name || selectedUser.username}`
                  : 'Envie uma mensagem para o chat geral'
                }
              </p>
            </div>
          )}

          {connected && searchFilteredMessages.length === 0 && searchTerm && (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Nenhuma mensagem encontrada</h3>
              <p className="text-gray-600">Tente buscar por outros termos</p>
            </div>
          )}

          {searchFilteredMessages.map(renderMessage)}

          {/* Indicador de digitação */}
          {userTyping && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg max-w-xs">
                <p className="text-sm">
                  <span className="font-medium">{userTyping.username}</span> está digitando
                  <span className="animate-pulse">...</span>
                </p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Área de input */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          {/* Picker de emojis */}
          {showEmojiPicker && (
            <div className="mb-3 p-3 bg-white border border-gray-200 rounded-lg shadow-lg">
              <div className="grid grid-cols-10 gap-2 max-h-40 overflow-y-auto">
                {popularEmojis.map((emoji, index) => (
                  <button
                    key={index}
                    onClick={() => addEmoji(emoji)}
                    className="text-xl hover:bg-gray-100 rounded p-1 transition-colors"
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSendMessage} className="flex space-x-3">
            <div className="flex space-x-2">
              {/* Botão de emoji */}
              <button
                type="button"
                onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                className="px-3 py-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                disabled={!connected}
              >
                😜
              </button>

              {/* Botão de arquivo */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                className="hidden"
                accept="image/*,.pdf,.txt,.doc,.docx"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={!connected || isUploading}
                className="px-3 py-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
              >
                {isUploading ? '⏳' : '📎'}
              </button>
            </div>

            <input
              type="text"
              value={newMessage}
              onChange={handleTyping}
              placeholder={
                selectedUser
                  ? `Mensagem para ${selectedUser.full_name || selectedUser.username}...`
                  : 'Digite sua mensagem...'
              }
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={!connected}
            />
            <button
              type="submit"
              disabled={!connected || !newMessage.trim() || isUploading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Enviar
            </button>
          </form>

          {!connected && (
            <p className="text-sm text-red-600 mt-2 text-center">
              Desconectado - Aguarde a reconexão para enviar mensagens
            </p>
          )}

          {isUploading && (
            <p className="text-sm text-blue-600 mt-2 text-center">
              Enviando arquivo... ⏳
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;