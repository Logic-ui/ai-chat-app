import { useState } from "react";
import { useChatSocket } from "./useChatSocket";
import "./App.css";

const sentimentColor = {
  positive: "#22c55e",
  neutral: "#94a3b8",
  negative: "#ef4444",
};

export default function App() {
  const [input, setInput] = useState("");
  const { messages, sendMessage, aiTyping } = useChatSocket("room-1");

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="chat-container">
      <h2>AI Support Chat</h2>
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.sender}`}>
            <span>{m.content}</span>
            {m.sender === "user" && (
              <span
                className="sentiment-dot"
                style={{ background: sentimentColor[m.sentiment] || "#94a3b8" }}
              />
            )}
          </div>
        ))}
        {aiTyping && <div className="bubble ai typing">AI is typing…</div>}
      </div>
      <div className="input-bar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}