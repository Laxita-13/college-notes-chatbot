import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

const askQuestion = async () => {
  if (!question.trim() || loading) return;

  const currentQuestion = question;

  setMessages((prev) => [
    ...prev,
    {
      type: "user",
      text: currentQuestion,
    },
  ]);

  setQuestion("");
  setLoading(true);


    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
        }),
      });

      const data = await response.json();

      // Add chatbot answer
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: data.answer,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Unable to connect to the backend.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <div className="chat-container">

        <h1>📚 College Notes Chatbot</h1>

        <p className="subtitle">
          Ask questions from your college notes
        </p>

        <div className="chat-box">

          {messages.length === 0 && (
            <p className="welcome">
              👋 Ask me something about your notes!
            </p>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.type}`}
            >
              <strong>
                {message.type === "user" ? "You" : "Bot"}
              </strong>

              <p>{message.text}</p>
            </div>
          ))}

          {loading && (
            <div className="message bot">
              <strong>Bot</strong>
              <p>Thinking...</p>
            </div>
          )}

        </div>

        <div className="input-area">

          <input
            type="text"
            placeholder="Ask something from your notes..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                askQuestion();
              }
            }}
          />

          <button
            onClick={askQuestion}
            disabled={loading}
          >
            {loading ? "..." : "Ask"}
          </button>

        </div>

      </div>
    </div>
  );
}

export default App;