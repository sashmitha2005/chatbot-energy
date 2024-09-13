import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    
    if (query.trim()) {
      // Add the user's query to the messages array
      setMessages([...messages, { text: query, sender: 'user' }]);
      
      // Send the query to the Flask backend
      try {
        const response = await axios.post('http://localhost:5000/chatbot', { query });
        const botResponse = response.data.response;

        // Check if the response is an empty object or contains an error message
        if (botResponse === "{}") {
          setMessages([...messages, { text: query, sender: 'user' }, { text: "No data found for the specified criteria.", sender: 'bot' }]);
        } else {
          // Add the bot's response to the messages array
          setMessages([...messages, { text: query, sender: 'user' }, { text: botResponse, sender: 'bot' }]);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        setMessages([...messages, { text: query, sender: 'user' }, { text: "Error fetching data. Please try again later.", sender: 'bot' }]);
      }

      setQuery('');  // Clear the input
    }
  };

  return (
    <div className="App">
      <h1>Energy Chatbot</h1>
      <div className="chat-window">
        {messages.map((message, index) => (
          <div key={index} className={`chat-message ${message.sender}`}>
            <p>{message.text}</p>
          </div>
        ))}
      </div>
      <form onSubmit={handleQuerySubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about solar or electricity data..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;
