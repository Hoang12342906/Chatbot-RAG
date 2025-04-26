import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import '../../styles/ChatPage.css';

function ChatPage() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [sessions, setSessions] = useState([]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const existingSession = localStorage.getItem('session_id');
    if (existingSession) {
      setSessionId(existingSession);
      loadMessages(existingSession);
    } else {
      const newSession = uuidv4();
      setSessionId(newSession);
      localStorage.setItem('session_id', newSession);
    }
    fetchSessions();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!question.trim()) return;

    const newMessage = { type: 'user', text: question };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    setQuestion('');
    setIsLoading(true);

    saveMessage(sessionId, 'user', question);

    try {
      const res = await axios.post('http://localhost:8000/chat', {
        question: question,
        history: updatedMessages,
      });
      const botReply = res.data.answer;
      setMessages((prev) => [...prev, { type: 'bot', text: botReply }]);
      saveMessage(sessionId, 'bot', botReply);
    } catch (err) {
      setMessages((prev) => [...prev, { type: 'bot', text: '❌ Lỗi server!' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const saveMessage = async (sessionId, sender, text) => {
    try {
      await axios.post('http://localhost:8000/save-message', {
        session_id: sessionId,
        sender: sender,
        message: text
      });
    } catch (error) {
      console.error('Lỗi khi lưu tin nhắn:', error);
    }
  };

  const loadMessages = async (sessionId) => {
    try {
      const res = await axios.get(`http://localhost:8000/load-messages?session_id=${sessionId}`);
      setMessages(res.data);
    } catch (error) {
      console.error('Lỗi tải lịch sử:', error);
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await axios.get('http://localhost:8000/list-sessions');
      setSessions(res.data);
    } catch (error) {
      console.error('Lỗi tải danh sách session:', error);
    }
  };

  const startNewSession = () => {
    const newSession = uuidv4();
    setSessionId(newSession);
    localStorage.setItem('session_id', newSession);
    setMessages([]);
  };

  return (
    <div className="chat-layout">
      <aside className="sidebar">
        <div className="logo">🤖 MyBot</div>
        <div className="history">
          <div>Lịch sử chat:</div>
          {sessions.map((sid, index) => (
            <div key={index} className="session-item" onClick={() => {
              setSessionId(sid);
              localStorage.setItem('session_id', sid);
              loadMessages(sid);
            }}>
              {sid.slice(0, 8)}...
            </div>
          ))}
          <button onClick={startNewSession}>➕ Phiên mới</button>
        </div>
      </aside>

      <main className="chat-main">
        <header className="chat-header">Chat với Tài liệu PDF</header>

        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.type}`}>
              <div className="text">{msg.text}</div>
            </div>
          ))}
          {isLoading && (
            <div className="chat-bubble bot loading">
              <div className="text">📝 Bot đang soạn câu trả lời...</div>
            </div>
          )}
          <div ref={chatEndRef}></div>
        </div>

        <div className="chat-input">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Nhập câu hỏi của bạn..."
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button onClick={handleSend}>➤</button>
        </div>
      </main>
    </div>
  );
}

export default ChatPage;