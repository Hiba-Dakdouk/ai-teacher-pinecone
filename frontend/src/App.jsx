import { useState } from 'react'
import { sendMessage } from './api'
import './App.css'
import DocumentUpload from './DocumentUpload'
import ReactMarkdown from 'react-markdown'

export default function App() {
  // 3 state variables here
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [documentName, setDocumentName] = useState('');


  async function handleSend() {
    // step 1: guard clause
    if (input.trim() === '' || loading) return;
    
    // step 2: create user message object { role: "user", content: input }
    const userMessage = { role: "user", content: input };
    
    // step 3: build updated messages array and store it in a variable
    const updatedMessages = [...messages, userMessage];
    
    // step 4: call setMessages with the updated array
    setMessages(updatedMessages);
    
    // step 5: clear input
    setInput('');

    // step 6: set loading to true
    setLoading(true);

    // step 7: try/finally
    //   - call sendMessage(updatedMessages), wait for reply
    try{
      setError(null);
      const reply = await sendMessage(updatedMessages);
      const assistantMessage = { role: "assistant", content: reply };
      setMessages([...updatedMessages, assistantMessage]);
    } catch (err) {
      console.error(err);
      setError("Failed to get response from the server. Please try again.");

    } finally {
      setLoading(false)
    }
    
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  async function handleDocumentLoaded(filename) {
    setDocumentName(filename);
    setMessages([]); // clear chat history when a new document is loaded
  }
  
  async function handleDocumentCleared() {
    setDocumentName('');
    setMessages([]); // clear chat history when document is cleared
  }

  return (
  <div className="app">

    <header>
      <h1>AI Teacher</h1>
      <p>Your personal AI learning assistant</p>
      <DocumentUpload
        onDocumentLoaded={handleDocumentLoaded}
        onDocumentCleared={handleDocumentCleared}
      />
    </header>


    <div className="chat-window">
      {messages.length === 0 && (
        <div className="welcome-message">
          <p>{documentName
            ? `📄 "${documentName}" loaded — ask me anything about it`
            : 'Upload a PDF or ask me any AI question'
          }</p>
        </div>
      )}
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.role}`}>
          <span className="label">{msg.role === 'user' ? 'You' : 'Teacher'}</span>
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>
      ))}
      {loading && (
        <div className="message assistant">
          <p>Thinking...</p>
        </div>
      )}
    </div>

    <div className="input-area">
      <textarea
        value={input}
        rows={3}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message here..."
      />
      <button onClick={handleSend} disabled={loading}>
        Send
      </button>
    </div>

  </div>
)
}

