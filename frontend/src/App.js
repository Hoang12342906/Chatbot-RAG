import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ChatPage from './components/user/ChatPage';
import AdminPage from './components/admin/AdminPage';



function App() {
  return (
    <Router>
    <div>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/admin" element={<AdminPage />} />

      </Routes>
    </div>
  </Router>
  );
}

export default App;
