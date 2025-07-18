import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  MessageCircle, 
  CheckSquare, 
  Target, 
  FileText, 
  Plus, 
  Send, 
  Mic, 
  MicOff,
  Trash2,
  Edit,
  Calendar,
  BarChart3
} from 'lucide-react'
import './App.css'

// const API_BASE_URL = 'https://backend-dev-dot-pure-album-439502-s4.uc.r.appspot.com/api' //for dev
const API_BASE_URL = 'https://backend-prod-dot-pure-album-439502-s4.uc.r.appspot.com/api'  //for prod

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [tasks, setTasks] = useState([])
  const [goals, setGoals] = useState([])
  const [notes, setNotes] = useState([])
  const [dashboard, setDashboard] = useState({})
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [loading, setLoading] = useState(false)

  // New task form
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    due_date: ''
  })

  // New goal form
  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    target_date: '',
    progress: 0
  })

  // New note form
  const [newNote, setNewNote] = useState({
    title: '',
    content: '',
    tags: []
  })

  useEffect(() => {
    loadDashboard()
    loadTasks()
    loadGoals()
    loadNotes()
    loadConversations()
  }, [])

  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('API call failed:', error)
      throw error
    }
  }

  const loadDashboard = async () => {
    try {
      const data = await apiCall('/dashboard?user_id=1')
      setDashboard(data)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    }
  }

  const loadTasks = async () => {
    try {
      const data = await apiCall('/tasks?user_id=1')
      setTasks(data)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }

  const loadGoals = async () => {
    try {
      const data = await apiCall('/goals?user_id=1')
      setGoals(data)
    } catch (error) {
      console.error('Failed to load goals:', error)
    }
  }

  const loadNotes = async () => {
    try {
      const data = await apiCall('/notes?user_id=1')
      setNotes(data)
    } catch (error) {
      console.error('Failed to load notes:', error)
    }
  }

  const loadConversations = async () => {
    try {
      const data = await apiCall('/conversations?user_id=1&limit=20')
      setChatHistory(data.reverse())
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }

  const sendMessage = async () => {
    if (!chatMessage.trim()) return

    setLoading(true)
    try {
      const response = await apiCall('/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: chatMessage,
          user_id: 1
        })
      })

      setChatHistory(prev => [...prev, {
        message: chatMessage,
        response: response.response,
        created_at: new Date().toISOString()
      }])
      
      setChatMessage('')
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setLoading(false)
    }
  }

  const createTask = async () => {
    if (!newTask.title.trim()) return

    try {
      await apiCall('/tasks', {
        method: 'POST',
        body: JSON.stringify({
          ...newTask,
          user_id: 1
        })
      })

      setNewTask({ title: '', description: '', priority: 'medium', due_date: '' })
      loadTasks()
      loadDashboard()
    } catch (error) {
      console.error('Failed to create task:', error)
    }
  }

  const updateTaskStatus = async (taskId, status) => {
    try {
      await apiCall(`/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify({ status })
      })
      loadTasks()
      loadDashboard()
    } catch (error) {
      console.error('Failed to update task:', error)
    }
  }

  const deleteTask = async (taskId) => {
    try {
      await apiCall(`/tasks/${taskId}`, {
        method: 'DELETE'
      })
      loadTasks()
      loadDashboard()
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  const createGoal = async () => {
    if (!newGoal.title.trim()) return

    try {
      await apiCall('/goals', {
        method: 'POST',
        body: JSON.stringify({
          ...newGoal,
          user_id: 1
        })
      })

      setNewGoal({ title: '', description: '', target_date: '', progress: 0 })
      loadGoals()
      loadDashboard()
    } catch (error) {
      console.error('Failed to create goal:', error)
    }
  }

  const updateGoalProgress = async (goalId, progress) => {
    try {
      await apiCall(`/goals/${goalId}`, {
        method: 'PUT',
        body: JSON.stringify({ progress })
      })
      loadGoals()
      loadDashboard()
    } catch (error) {
      console.error('Failed to update goal:', error)
    }
  }

  const createNote = async () => {
    if (!newNote.title.trim() && !newNote.content.trim()) return

    try {
      await apiCall('/notes', {
        method: 'POST',
        body: JSON.stringify({
          ...newNote,
          user_id: 1
        })
      })

      setNewNote({ title: '', content: '', tags: [] })
      loadNotes()
      loadDashboard()
    } catch (error) {
      console.error('Failed to create note:', error)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      const chunks = []

      recorder.ondataavailable = (event) => {
        chunks.push(event.data)
      }

      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/wav' })
        await uploadVoiceNote(blob)
        stream.getTracks().forEach(track => track.stop())
      }

      recorder.start()
      setMediaRecorder(recorder)
      setIsRecording(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
      alert('Failed to access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop()
      setIsRecording(false)
      setMediaRecorder(null)
    }
  }

  const uploadVoiceNote = async (audioBlob) => {
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'voice_note.wav')
      formData.append('user_id', '1')
      formData.append('title', `Voice Note ${new Date().toLocaleString()}`)

      await fetch(`${API_BASE_URL}/notes/voice`, {
        method: 'POST',
        body: formData
      })

      loadNotes()
      loadDashboard()
    } catch (error) {
      console.error('Failed to upload voice note:', error)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'No date'
    return new Date(dateString).toLocaleDateString()
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'pending': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Master Agent</h1>
          <p className="text-gray-600">Your Personal AI Assistant</p>
        </header>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="w-4 h-4" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="tasks" className="flex items-center gap-2">
              <CheckSquare className="w-4 h-4" />
              Tasks
            </TabsTrigger>
            <TabsTrigger value="goals" className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Goals
            </TabsTrigger>
            <TabsTrigger value="notes" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Notes
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckSquare className="w-5 h-5" />
                    Tasks
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Total:</span>
                      <span className="font-semibold">{dashboard.tasks?.total || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Completed:</span>
                      <span className="text-green-600">{dashboard.tasks?.completed || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Pending:</span>
                      <span className="text-orange-600">{dashboard.tasks?.pending || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Goals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Total:</span>
                      <span className="font-semibold">{dashboard.goals?.total || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Active:</span>
                      <span className="text-blue-600">{dashboard.goals?.active || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Completed:</span>
                      <span className="text-green-600">{dashboard.goals?.completed || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Notes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Total:</span>
                      <span className="font-semibold">{dashboard.notes?.total || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Text:</span>
                      <span className="text-blue-600">{dashboard.notes?.text || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Voice:</span>
                      <span className="text-purple-600">{dashboard.notes?.voice || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Tasks</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboard.tasks?.recent?.slice(0, 5).map(task => (
                      <div key={task.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">{task.title}</span>
                        <Badge className={getStatusColor(task.status)}>
                          {task.status}
                        </Badge>
                      </div>
                    )) || <p className="text-gray-500">No recent tasks</p>}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboard.notes?.recent?.slice(0, 5).map(note => (
                      <div key={note.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">{note.title || 'Untitled'}</span>
                        <Badge variant="outline">
                          {note.note_type}
                        </Badge>
                      </div>
                    )) || <p className="text-gray-500">No recent notes</p>}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-4">
            <Card className="h-96">
              <CardHeader>
                <CardTitle>Chat with Master Agent</CardTitle>
              </CardHeader>
              <CardContent className="h-full flex flex-col">
                <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                  {chatHistory.map((chat, index) => (
                    <div key={index} className="space-y-2">
                      <div className="bg-blue-100 p-3 rounded-lg ml-auto max-w-xs">
                        <p className="text-sm">{chat.message}</p>
                      </div>
                      <div className="bg-gray-100 p-3 rounded-lg mr-auto max-w-xs">
                        <p className="text-sm">{chat.response}</p>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="bg-gray-100 p-3 rounded-lg mr-auto max-w-xs">
                      <p className="text-sm">Thinking...</p>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    placeholder="Type your message..."
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    disabled={loading}
                  />
                  <Button onClick={sendMessage} disabled={loading || !chatMessage.trim()}>
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tasks Tab */}
          <TabsContent value="tasks" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Create New Task</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Task title"
                  value={newTask.title}
                  onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                />
                <Textarea
                  placeholder="Task description"
                  value={newTask.description}
                  onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                />
                <div className="flex gap-4">
                  <Select value={newTask.priority} onValueChange={(value) => setNewTask({...newTask, priority: value})}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    type="date"
                    value={newTask.due_date}
                    onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                  />
                  <Button onClick={createTask}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Task
                  </Button>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-4">
              {tasks.map(task => (
                <Card key={task.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold">{task.title}</h3>
                        <p className="text-sm text-gray-600">{task.description}</p>
                        <div className="flex gap-2 mt-2">
                          <Badge className={getPriorityColor(task.priority)}>
                            {task.priority}
                          </Badge>
                          <Badge className={getStatusColor(task.status)}>
                            {task.status}
                          </Badge>
                          {task.due_date && (
                            <Badge variant="outline">
                              <Calendar className="w-3 h-3 mr-1" />
                              {formatDate(task.due_date)}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {task.status !== 'completed' && (
                          <Button
                            size="sm"
                            onClick={() => updateTaskStatus(task.id, 'completed')}
                          >
                            Complete
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => deleteTask(task.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Goals Tab */}
          <TabsContent value="goals" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Create New Goal</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Goal title"
                  value={newGoal.title}
                  onChange={(e) => setNewGoal({...newGoal, title: e.target.value})}
                />
                <Textarea
                  placeholder="Goal description"
                  value={newGoal.description}
                  onChange={(e) => setNewGoal({...newGoal, description: e.target.value})}
                />
                <div className="flex gap-4">
                  <Input
                    type="date"
                    placeholder="Target date"
                    value={newGoal.target_date}
                    onChange={(e) => setNewGoal({...newGoal, target_date: e.target.value})}
                  />
                  <Button onClick={createGoal}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Goal
                  </Button>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-4">
              {goals.map(goal => (
                <Card key={goal.id}>
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{goal.title}</h3>
                        <Badge className={goal.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}>
                          {goal.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{goal.description}</p>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Progress</span>
                          <span>{goal.progress}%</span>
                        </div>
                        <Progress value={goal.progress} className="w-full" />
                      </div>
                      {goal.target_date && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Calendar className="w-4 h-4" />
                          Target: {formatDate(goal.target_date)}
                        </div>
                      )}
                      <div className="flex gap-2">
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          placeholder="Progress %"
                          className="w-24"
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              const progress = parseInt(e.target.value)
                              if (progress >= 0 && progress <= 100) {
                                updateGoalProgress(goal.id, progress)
                                e.target.value = ''
                              }
                            }
                          }}
                        />
                        <Button
                          size="sm"
                          onClick={() => {
                            const input = document.querySelector(`input[placeholder="Progress %"]`)
                            const progress = parseInt(input.value)
                            if (progress >= 0 && progress <= 100) {
                              updateGoalProgress(goal.id, progress)
                              input.value = ''
                            }
                          }}
                        >
                          Update
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Notes Tab */}
          <TabsContent value="notes" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Create New Note</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Note title"
                  value={newNote.title}
                  onChange={(e) => setNewNote({...newNote, title: e.target.value})}
                />
                <Textarea
                  placeholder="Note content"
                  value={newNote.content}
                  onChange={(e) => setNewNote({...newNote, content: e.target.value})}
                  rows={4}
                />
                <div className="flex gap-2">
                  <Button onClick={createNote}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Text Note
                  </Button>
                  <Button
                    onClick={isRecording ? stopRecording : startRecording}
                    variant={isRecording ? "destructive" : "outline"}
                  >
                    {isRecording ? (
                      <>
                        <MicOff className="w-4 h-4 mr-2" />
                        Stop Recording
                      </>
                    ) : (
                      <>
                        <Mic className="w-4 h-4 mr-2" />
                        Record Voice Note
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-4">
              {notes.map(note => (
                <Card key={note.id}>
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{note.title || 'Untitled'}</h3>
                        <div className="flex gap-2">
                          <Badge variant="outline">
                            {note.note_type === 'voice' ? (
                              <>
                                <Mic className="w-3 h-3 mr-1" />
                                Voice
                              </>
                            ) : (
                              <>
                                <FileText className="w-3 h-3 mr-1" />
                                Text
                              </>
                            )}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {formatDate(note.created_at)}
                          </span>
                        </div>
                      </div>
                      {note.content && (
                        <p className="text-sm text-gray-700">{note.content}</p>
                      )}
                      {note.transcription && (
                        <div className="bg-gray-50 p-2 rounded text-sm">
                          <strong>Transcription:</strong> {note.transcription}
                        </div>
                      )}
                      {note.tags && note.tags.length > 0 && (
                        <div className="flex gap-1 flex-wrap">
                          {note.tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

