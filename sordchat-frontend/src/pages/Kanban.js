import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import toast from 'react-hot-toast';

const Kanban = () => {
  const { user } = useAuth();

  const [boards, setBoards] = useState([]);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const [boardData, setBoardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showNewBoardModal, setShowNewBoardModal] = useState(false);
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');

  // Carregar quadros
  const loadBoards = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8001/kanban/boards', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setBoards(data);

        // Selecionar primeiro quadro se não houver selecionado
        if (!selectedBoard && data.length > 0) {
          setSelectedBoard(data[0].id);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar quadros:', error);
      toast.error('Erro ao carregar quadros');
    }
  }, [selectedBoard]);

  // Carregar dados do quadro específico
  const loadBoardData = useCallback(async (boardId) => {
    if (!boardId) return;

    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:8001/kanban/boards/${boardId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setBoardData(data);
      }
    } catch (error) {
      console.error('Erro ao carregar quadro:', error);
      toast.error('Erro ao carregar quadro');
    } finally {
      setLoading(false);
    }
  }, []);

  // Criar novo quadro
  const createBoard = async (boardData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8001/kanban/boards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(boardData),
      });

      if (response.ok) {
        const result = await response.json();
        toast.success('Quadro criado com sucesso! 📋');
        loadBoards();
        setShowNewBoardModal(false);
        setSelectedBoard(result.board_id);
      }
    } catch (error) {
      console.error('Erro ao criar quadro:', error);
      toast.error('Erro ao criar quadro');
    }
  };

  // Criar nova tarefa
  const createTask = async (taskData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8001/kanban/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...taskData,
          board_id: selectedBoard,
          column_id: selectedColumn,
        }),
      });

      if (response.ok) {
        toast.success('Tarefa criada com sucesso! ✅');
        loadBoardData(selectedBoard);
        setShowNewTaskModal(false);
        setSelectedColumn(null);
      }
    } catch (error) {
      console.error('Erro ao criar tarefa:', error);
      toast.error('Erro ao criar tarefa');
    }
  };

  // Mover tarefa (drag & drop)
  const moveTask = async (taskId, newColumnId, newPosition) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:8001/kanban/tasks/${taskId}/move`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          column_id: newColumnId,
          position: newPosition,
        }),
      });

      if (response.ok) {
        loadBoardData(selectedBoard);
      }
    } catch (error) {
      console.error('Erro ao mover tarefa:', error);
      toast.error('Erro ao mover tarefa');
    }
  };

  // Atualizar tarefa
  const updateTask = async (taskId, taskData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:8001/kanban/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(taskData),
      });

      if (response.ok) {
        toast.success('Tarefa atualizada com sucesso! 📝');
        loadBoardData(selectedBoard);
        setShowTaskModal(false);
        setSelectedTask(null);
      }
    } catch (error) {
      console.error('Erro ao atualizar tarefa:', error);
      toast.error('Erro ao atualizar tarefa');
    }
  };

  // Deletar tarefa
  const deleteTask = async (taskId) => {
    if (!window.confirm('Tem certeza que deseja deletar esta tarefa?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:8001/kanban/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        toast.success('Tarefa deletada com sucesso! 🗑️');
        loadBoardData(selectedBoard);
        setShowTaskModal(false);
        setSelectedTask(null);
      }
    } catch (error) {
      console.error('Erro ao deletar tarefa:', error);
      toast.error('Erro ao deletar tarefa');
    }
  };

  // Handle drag & drop
  const onDragEnd = (result) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const taskId = parseInt(draggableId);
    const newColumnId = parseInt(destination.droppableId);
    const newPosition = destination.index + 1;

    moveTask(taskId, newColumnId, newPosition);
  };

  // Filtrar tarefas
  const filterTasks = (tasks) => {
    return tasks.filter(task => {
      const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           task.description?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
      const matchesCategory = filterCategory === 'all' || task.category === filterCategory;

      return matchesSearch && matchesPriority && matchesCategory;
    });
  };

  // Obter cor da prioridade
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Obter ícone da prioridade
  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  // Formatar data
  const formatDate = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  // Verificar se está atrasado
  const isOverdue = (dueDate) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  // Effects
  useEffect(() => {
    loadBoards();
  }, [loadBoards]);

  useEffect(() => {
    if (selectedBoard) {
      loadBoardData(selectedBoard);
    }
  }, [selectedBoard, loadBoardData]);

  // Obter categorias únicas
  const getUniqueCategories = () => {
    if (!boardData?.columns) return [];
    const categories = new Set();
    boardData.columns.forEach(column => {
      column.tasks.forEach(task => {
        if (task.category) categories.add(task.category);
      });
    });
    return Array.from(categories);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Carregando Kanban...</h3>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-800">📋 Kanban</h1>

            {/* Seletor de quadro */}
            <select
              value={selectedBoard || ''}
              onChange={(e) => setSelectedBoard(parseInt(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecione um quadro</option>
              {boards.map(board => (
                <option key={board.id} value={board.id}>
                  {board.name}
                </option>
              ))}
            </select>

            <button
              onClick={() => setShowNewBoardModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Novo Quadro
            </button>
          </div>

          <div className="text-sm text-gray-600">
            {boardData && (
              <span>
                {boardData.columns?.reduce((total, col) => total + col.tasks.length, 0)} tarefas
              </span>
            )}
          </div>
        </div>

        {/* Filtros */}
        <div className="flex items-center space-x-4">
          <input
            type="text"
            placeholder="Buscar tarefas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todas as prioridades</option>
            <option value="high">Alta prioridade</option>
            <option value="medium">Média prioridade</option>
            <option value="low">Baixa prioridade</option>
          </select>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todas as categorias</option>
            {getUniqueCategories().map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Board Content */}
      {!selectedBoard ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">📋</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Selecione um quadro</h3>
            <p className="text-gray-600 mb-4">Escolha um quadro para visualizar as tarefas</p>
            <button
              onClick={() => setShowNewBoardModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Criar Primeiro Quadro
            </button>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-hidden">
          <DragDropContext onDragEnd={onDragEnd}>
            <div className="h-full overflow-x-auto">
              <div className="flex space-x-6 p-6 min-w-max">
                {boardData?.columns?.map((column) => (
                  <div
                    key={column.id}
                    className="w-80 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col"
                  >
                    {/* Column Header */}
                    <div
                      className="p-4 border-b border-gray-200 flex items-center justify-between"
                      style={{ borderTopColor: column.color, borderTopWidth: '3px' }}
                    >
                      <h3 className="font-semibold text-gray-800">{column.name}</h3>
                      <div className="flex items-center space-x-2">
                        <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                          {filterTasks(column.tasks).length}
                        </span>
                        <button
                          onClick={() => {
                            setSelectedColumn(column.id);
                            setShowNewTaskModal(true);
                          }}
                          className="text-gray-400 hover:text-gray-600 transition-colors"
                        >
                          +
                        </button>
                      </div>
                    </div>

                    {/* Tasks */}
                    <Droppable droppableId={column.id.toString()}>
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.droppableProps}
                          className={`flex-1 p-4 space-y-3 min-h-[200px] ${
                            snapshot.isDraggingOver ? 'bg-blue-50' : ''
                          }`}
                        >
                          {filterTasks(column.tasks).map((task, index) => (
                            <Draggable
                              key={task.id}
                              draggableId={task.id.toString()}
                              index={index}
                            >
                              {(provided, snapshot) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                  onClick={() => {
                                    setSelectedTask(task);
                                    setShowTaskModal(true);
                                  }}
                                  className={`p-3 bg-white border border-gray-200 rounded-lg cursor-pointer hover:shadow-md transition-shadow ${
                                    snapshot.isDragging ? 'shadow-lg rotate-2' : ''
                                  }`}
                                >
                                  {/* Task Header */}
                                  <div className="flex items-start justify-between mb-2">
                                    <h4 className="font-medium text-gray-800 text-sm line-clamp-2">
                                      {task.title}
                                    </h4>
                                    <span className="text-lg ml-2">
                                      {getPriorityIcon(task.priority)}
                                    </span>
                                  </div>

                                  {/* Task Description */}
                                  {task.description && (
                                    <p className="text-xs text-gray-600 mb-2 line-clamp-2">
                                      {task.description}
                                    </p>
                                  )}

                                  {/* Task Meta */}
                                  <div className="flex items-center justify-between text-xs">
                                    <div className="flex items-center space-x-2">
                                      {task.category && (
                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                                          {task.category}
                                        </span>
                                      )}

                                      {task.due_date && (
                                        <span className={`px-2 py-1 rounded-full ${
                                          isOverdue(task.due_date)
                                            ? 'bg-red-100 text-red-800'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}>
                                          📅 {formatDate(task.due_date)}
                                        </span>
                                      )}
                                    </div>

                                    {task.assigned_to_name && (
                                      <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-medium text-blue-600">
                                          {task.assigned_to_name.charAt(0)}
                                        </span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}
                            </Draggable>
                          ))}
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                  </div>
                ))}
              </div>
            </div>
          </DragDropContext>
        </div>
      )}

      {/* Modals */}
      {showNewBoardModal && (
        <NewBoardModal
          onClose={() => setShowNewBoardModal(false)}
          onSubmit={createBoard}
        />
      )}

      {showNewTaskModal && (
        <NewTaskModal
          onClose={() => {
            setShowNewTaskModal(false);
            setSelectedColumn(null);
          }}
          onSubmit={createTask}
        />
      )}

      {showTaskModal && selectedTask && (
        <TaskModal
          task={selectedTask}
          onClose={() => {
            setShowTaskModal(false);
            setSelectedTask(null);
          }}
          onUpdate={updateTask}
          onDelete={deleteTask}
        />
      )}
    </div>
  );
};

// Modal para novo quadro
const NewBoardModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#3B82F6'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error('Nome do quadro é obrigatório');
      return;
    }
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Novo Quadro</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nome do Quadro *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Projeto Principal"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descrição
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Descrição do quadro..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cor
            </label>
            <div className="flex space-x-2">
              {['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'].map(color => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, color }))}
                  className={`w-8 h-8 rounded-full border-2 ${
                    formData.color === color ? 'border-gray-800' : 'border-gray-300'
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Criar Quadro
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Modal para nova tarefa
const NewTaskModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: '',
    due_date: '',
    assigned_to: null
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      toast.error('Título da tarefa é obrigatório');
      return;
    }
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">Nova Tarefa</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Título *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Implementar login"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descrição
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Descrição da tarefa..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prioridade
            </label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">🟢 Baixa</option>
              <option value="medium">🟡 Média</option>
              <option value="high">🔴 Alta</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoria
            </label>
            <input
              type="text"
              value={formData.category}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Frontend, Backend, Bug..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data de Vencimento
            </label>
            <input
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Criar Tarefa
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Modal para visualizar/editar tarefa
const TaskModal = ({ task, onClose, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    title: task.title,
    description: task.description || '',
    priority: task.priority,
    category: task.category || '',
    due_date: task.due_date ? task.due_date.split('T')[0] : '',
    assigned_to: task.assigned_to
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      toast.error('Título da tarefa é obrigatório');
      return;
    }
    onUpdate(task.id, formData);
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Não definido';
    return new Date(dateString).toLocaleString('pt-BR');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">
            {isEditing ? 'Editar Tarefa' : 'Detalhes da Tarefa'}
          </h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded"
            >
              {isEditing ? 'Cancelar' : 'Editar'}
            </button>
            <button
              onClick={() => onDelete(task.id)}
              className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
            >
              Deletar
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
        </div>

        {isEditing ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Título *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descrição
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="4"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Prioridade
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">🟢 Baixa</option>
                  <option value="medium">🟡 Média</option>
                  <option value="high">🔴 Alta</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Categoria
                </label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data de Vencimento
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Salvar Alterações
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-800 text-lg mb-2">{task.title}</h4>
              {task.description && (
                <p className="text-gray-600 whitespace-pre-wrap">{task.description}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Prioridade:</span>
                <div className="mt-1">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                    task.priority === 'high' ? 'bg-red-100 text-red-800' :
                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {task.priority === 'high' ? '🔴 Alta' :
                     task.priority === 'medium' ? '🟡 Média' :
                     '🟢 Baixa'}
                  </span>
                </div>
              </div>

              <div>
                <span className="font-medium text-gray-700">Categoria:</span>
                <p className="mt-1 text-gray-600">{task.category || 'Não definida'}</p>
              </div>

              <div>
                <span className="font-medium text-gray-700">Vencimento:</span>
                <p className={`mt-1 ${
                  task.due_date && new Date(task.due_date) < new Date() 
                    ? 'text-red-600 font-medium' 
                    : 'text-gray-600'
                }`}>
                  {task.due_date ? formatDateTime(task.due_date) : 'Não definido'}
                </p>
              </div>

              <div>
                <span className="font-medium text-gray-700">Responsável:</span>
                <p className="mt-1 text-gray-600">{task.assigned_to_name || 'Não atribuído'}</p>
              </div>

              <div>
                <span className="font-medium text-gray-700">Criado por:</span>
                <p className="mt-1 text-gray-600">{task.created_by_name}</p>
              </div>

              <div>
                <span className="font-medium text-gray-700">Criado em:</span>
                <p className="mt-1 text-gray-600">{formatDateTime(task.created_at)}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Kanban;