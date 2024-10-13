import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // WebSocket 연결 설정
    const socket = new WebSocket('wss://welfarebot.kr/react');

    socket.onopen = () => {
      console.log('WebSocket 연결 성공');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'transcription') {
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'user', text: data.transcription },
        ]);
      } else if (data.event === 'sttCorrection') {
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'user', text: `수정된 텍스트: ${data.sttCorrectionModelResponse}` },
        ]);
      } else if (data.event === 'gptResponse') {
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'gpt', text: data.chatModelResponse },
        ]);
      } else if (data.event === 'chatSummary') {
        setMessages((prevMessages) => [
          ...prevMessages,
          {type:'gpt', text: `대화 내용 요약: ${data.chatSummaryModelResponse}` },
        ]);
      }
    };

    socket.onclose = () => {
      console.log('WebSocket 연결 종료');
    };
    
    // 컴포넌트가 언마운트될 때 WebSocket 연결 해제
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="chat-container">
      {messages.map((message, index) =>(
        <div
          key={index}
          className={message.type === 'user' ? 'user-message' : 'gpt-message'}
        >
          {message.text}
          </div>
          ))}
    </div>
  );
}

export default App;
