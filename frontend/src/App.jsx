import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import styles from './App.module.css'
import MessageBubble from './components/MessageBubble'
import AuthModal from './components/AuthModal'
import Sidebar from './components/Sidebar'

function App() {
  const [input, setInput] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [activeChat, setActiveChat] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [allChatsData, setAllChatsData] = useState({})
  const [user, setUser] = useState(null)
  const [isAuthMode, setIsAuthMode] = useState(false)
  const [authData, setAuthData] = useState({ login: '', password: '' })
  const [authError, setAuthError] = useState('')
  
  const messagesEndRef = useRef(null)
  const currentMessages = activeChat ? (allChatsData[activeChat] || []) : []

  useEffect(() => {
    const token = localStorage.getItem("token")
    const savedUser = localStorage.getItem("userName")
    if (token && savedUser) {
      setUser(savedUser)
      fetchHistory()
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [currentMessages, isLoading])

  const startNewChat = () => {
    const newChatName = `Chat ${chatHistory.length + 1}`
    setChatHistory(prev => [newChatName, ...prev])
    setActiveChat(newChatName)
    setAllChatsData(prev => ({ ...prev, [newChatName]: [] }))
    localStorage.setItem("lastActiveChat", newChatName)
  }

  const fetchHistory = async () => {
    const token = localStorage.getItem("token")
    if (!token) return
    try {
      const response = await axios.get(`http://localhost:8000/history`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = response.data
  
      if (data && data.length > 0) {
        const groupedChats = {}
        const namesList = []
        data.forEach(item => {
          if (!groupedChats[item.chat_name]) {
            groupedChats[item.chat_name] = []
            namesList.push(item.chat_name)
          }
          groupedChats[item.chat_name].push({ role: 'user', content: item.text })
          groupedChats[item.chat_name].push({ role: 'assistant', content: item.sentiment })
        });
        setAllChatsData(groupedChats)
        setChatHistory(namesList)
        const lastChat = localStorage.getItem("lastActiveChat")
        setActiveChat(lastChat && namesList.includes(lastChat) ? lastChat : namesList[0])
      } else {
        // jeśli historia jest pusta (nowy użytkownik), otwieram czat automatycznie
        startNewChat()
      }
    } catch (err) {
      if (err.response?.status === 401) handleLogout()
    }
  }

  const handleAuth = async (type) => {
    setAuthError('')
    try {
      const response = await axios.post(`http://localhost:8000/${type}`, authData)
      if (type === 'login') {
        localStorage.setItem("token", response.data.access_token)
        localStorage.setItem("userName", response.data.login)
        setUser(response.data.login)
        setIsAuthMode(false)
        setChatHistory([])
        setAllChatsData({})
        fetchHistory()
      } else {
        alert("Account created! Now please sign in.")
      }
    } catch (err) {
      setAuthError(err.response?.data?.detail || "Auth failed")
    }
  }

  const handleDeleteChat = async (chatName) => {
    // pytam użytkownika, czy na pewno usunac chat
    if (!window.confirm(`Are you sure you want to delete "${chatName}"?`)) return;
  
    const token = localStorage.getItem("token");
    try {
      // strzał do backendu
      await axios.delete(`http://localhost:8000/chat/${encodeURIComponent(chatName)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
  
      // usuwam z lokalnego stanu, żeby zniknęło z ekranu bez odświeżania
      setChatHistory(prev => prev.filter(name => name !== chatName));
      setAllChatsData(prev => {
        const newData = { ...prev };
        delete newData[chatName];
        return newData;
      });
  
      // jeśli usuwam aktualnie otwarty czat, czyszcze widok
      if (activeChat === chatName) setActiveChat(null);
      
    } catch (err) {
      console.error("Delete failed:", err);
      alert("Could not delete chat from server.");
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !activeChat || !user) return
    const query = input
    const token = localStorage.getItem("token")
    setInput('')
    setIsLoading(true)

    let currentChatName = activeChat
    if (activeChat.startsWith('Chat ')) {
      const newName = query.substring(0, 20) + (query.length > 20 ? '...' : '')
      setChatHistory(prev => prev.map(name => name === activeChat ? newName : name))
      setAllChatsData(prev => {
        const newData = { ...prev }
        newData[newName] = newData[activeChat] || []
        delete newData[activeChat]
        return newData
      })
      setActiveChat(newName)
      currentChatName = newName
      localStorage.setItem("lastActiveChat", newName)
    }

    setAllChatsData(prev => ({
      ...prev,
      [currentChatName]: [...(prev[currentChatName] || []), { role: 'user', content: query }]
    }))

    try {
      const response = await axios.post(
        `http://localhost:8000/analyze/?chat_name=${encodeURIComponent(currentChatName)}`,
        { text: query, source: "web_ui" },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setAllChatsData(prev => ({
        ...prev,
        [currentChatName]: [...(prev[currentChatName] || []), { role: 'assistant', content: response.data.sentiment }]
      }))
    } catch (e) {
      if (e.response?.status === 401) handleLogout()
    }
    setIsLoading(false)
  }

  const handleLogout = () => {
    localStorage.clear()
    setUser(null); setChatHistory([]); setAllChatsData({}); setActiveChat(null)
  }

  

  return (
    <div className={styles.appContainer}>
      <Sidebar 
        chatHistory={chatHistory} 
        activeChat={activeChat} 
        setActiveChat={setActiveChat} 
        startNewChat={startNewChat}
        onDeleteChat={handleDeleteChat} 
      />

      <main className={styles.mainContent}>
        <header className={styles.header}>
          {!user ? (
            <button onClick={() => setIsAuthMode(true)} className={styles.signInBtn}>Sign In</button>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '14px', color: '#aaa' }}>Logged as: <b style={{color: '#fff'}}>{user}</b></span>
              <button onClick={handleLogout} className={styles.logoutBtn}>Logout</button>
            </div>
          )}
        </header>

        <div className={styles.messagesContainer}>
          {/* ekran powitalny */}
          {currentMessages.length === 0 && (
            <div className={styles.welcomeScreen}>
              <h1 style={{ fontSize: '38px', opacity: 0.8 }}>{user ? `Hello ${user}` : "Sign In to chat"}</h1>
            </div>
          )}

          {/* mapuje istniejące wiadomości */}
          {currentMessages.map((msg, i) => (
            <MessageBubble key={i} msg={msg} />
          ))}

          {/* LOADER */}
          {isLoading && (
            <div className={styles.botTyping}>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
              <em style={{marginLeft: '10px', fontSize: '13px', color: '#aaa'}}>
                AI is thinking...
              </em>
            </div>
          )}

          {/* kotwica do scrollowania */}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputWrapper}>
          <div className={styles.inputBar}>
            <input 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()} 
              placeholder={user ? "Ask anything..." : "Sign in first"} 
              disabled={!activeChat || !user} 
              className={styles.chatInput}
            />
            <button 
              onClick={handleSendMessage} 
              disabled={!user} 
              className={styles.sendBtn}
              style={{ // zmieniam tło na białe tylko gdy jest tekst, w przeciwnym razie szare
                backgroundColor: (user && input.trim()) ? '#fff' : '#676767',
                // czarna strzałka na białym tle, jasnoszara na ciemnym
                color: (user && input.trim()) ? '#000' : '#aaa',
                cursor: (user && input.trim()) ? 'pointer' : 'default'}}
            >↑</button>
          </div>
        </div>
      </main>

      {isAuthMode && (
        <AuthModal 
          authData={authData} setAuthData={setAuthData} 
          handleAuth={handleAuth} setIsAuthMode={setIsAuthMode} 
          authError={authError} 
        />
      )}
    </div>
  )
}

export default App