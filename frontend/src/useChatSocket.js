import { useEffect, useRef, useState, useCallback } from "react";

export function useChatSocket(roomId) {
  const [messages, setMessages] = useState([]);
  const [aiTyping, setAiTyping] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    fetch(`http://localhost:8000/history/${roomId}`)
      .then(res => res.json())
      .then(setMessages);

    const ws = new WebSocket(`ws://localhost:8000/ws/${roomId}`);
    socketRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.typing !== undefined) {
        setAiTyping(data.typing);
        return;
      }
      setMessages(prev => [...prev, data]);
    };

    return () => ws.close();
  }, [roomId]);

  const sendMessage = useCallback((content) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ content }));
    }
  }, []);

  return { messages, sendMessage, aiTyping };
}