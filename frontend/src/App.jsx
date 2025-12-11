import React, { useState, useCallback } from 'react';
import './App.css'; // We'll create this file in the next step

const BACKEND_URL = "http://127.0.0.1:8000"; // Your FastAPI URL

function App() {
  // State for the current message the user is typing
  const [inputMessage, setInputMessage] = useState('');
  
  // State for the chat history (stores both user input and API response)
  const [chatHistory, setChatHistory] = useState([]);
  
  // State to track loading status
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle the message submission
  const handleSendMessage = useCallback(async (e) => {
    e.preventDefault(); // Prevents the default form submission behavior

    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    
    // 1. Add the user's message to the history
    setChatHistory(prev => [...prev, { sender: 'user', text: userMessage }]);
    setInputMessage(''); // Clear the input box
    setIsLoading(true);

    try {
      // 2. Send the message to the FastAPI backend's /chat endpoint
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      // 3. Add the LLM's response to the history
      const botResponse = data.response || "Error: No response received from agent.";
      setChatHistory(prev => [...prev, { sender: 'bot', text: botResponse }]);

    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => [...prev, { sender: 'bot', text: `Error: Failed to connect to backend or LLM. (${error.message})` }]);
    } finally {
      setIsLoading(false);
    }
  }, [inputMessage, isLoading]);

  return (
    <div className="app-container">
      <header>
        <h1>SanchAI Weather Agent 🌦️</h1>
        <p>Ask for the weather of any city (e.g., "weather of Pune today?").</p>
      </header>

      <div className="chat-window">
        {chatHistory.length === 0 ? (
          <div className="welcome-message">
            Type a message below to start!
          </div>
        ) : (
          // Display all messages in the history
          chatHistory.map((msg, index) => (
            <div key={index} className={`message-bubble ${msg.sender}`}>
              <span className="sender-tag">{msg.sender === 'user' ? 'You' : 'Agent'}</span>
              <p>{msg.text}</p>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message-bubble bot loading">
            <span className="sender-tag">Agent</span>
            <p>Thinking...</p>
          </div>
        )}
      </div>

      {/* Input box and send button */}
      <form onSubmit={handleSendMessage} className="input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="What's the weather of [City]?"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

export default App;