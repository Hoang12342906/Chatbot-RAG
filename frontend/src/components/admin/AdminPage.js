import React, { useState } from 'react';
import axios from 'axios';
import '../../styles/AdminPage.css';

function AdminPage() {
  const [files, setFiles] = useState([]);
  const [messages, setMessages] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
    setMessages([]);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    setUploading(true);
    try {
      const res = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setMessages(res.data.messages || ["✅ Tải lên thành công."]);
    } catch (error) {
      setMessages(["❌ Lỗi khi tải lên."]);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="admin-layout">
      <aside className="sidebar">
        <div className="logo">📁 Admin</div>
      </aside>

      <main className="admin-main">
        <header className="admin-header">Tải lên tài liệu PDF</header>

        <div className="upload-section">
          <input
            type="file"
            accept="application/pdf"
            multiple
            onChange={handleFileChange}
          />

          {files.length > 0 && (
            <ul className="file-list">
              {files.map((file, i) => (
                <li key={i}>{file.name}</li>
              ))}
            </ul>
          )}

          <button onClick={handleUpload} disabled={uploading}>
            {uploading ? 'Đang tải...' : 'Tải lên'}
          </button>

          <div className="messages">
            {messages.map((msg, i) => (
              <div key={i}>{msg}</div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default AdminPage;
