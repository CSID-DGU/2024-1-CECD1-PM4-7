import React, { useState, useEffect } from 'react';
import './App.css';
import botIcon from './logo_black.png';
import userIcon from './user.png';

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
          { type: 'user', text: `원문: ${data.transcription}`, isTranscription: true },
        ]);
      } else if (data.event === 'sttCorrection') {
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'user', text: `수정된 텍스트: ${data.sttCorrectionModelResponse}`, isTranscription: false},
        ]);
      } else if (data.event === 'gptResponse') {
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'gpt', text: data.chatModelResponse, isChatSummary: false },
        ]);
      } else if (data.event === 'chatSummary') {
        setMessages((prevMessages) => [
          ...prevMessages,
          {type:'gpt', text: `대화 내용 요약: ${data.chatSummaryModelResponse}`, isChatSummary: true },
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
    <div className="chat-frame">
      <div className="header">
        <div className="bot-info">
          <img src={botIcon} alt="복지봇" className="bot-header-icon" />
          <span className="bot-header-name">복지봇</span>
        </div>
      </div>

      <div className="basic-message">
        모든 대화는 인공지능 알고리즘에 의해 자동<br /> 생성되는 것으로 사실과 다를 수 있습니다.
      </div>

      <div className="date">2024.10.14</div>

      <div className="chat-container">
        {messages.map((message, index) => (
          <div key={index} className={message.type === 'user' ? 'user-message-container' : 'gpt-message-container'}>
            {message.type === 'gpt' && (
              <div className="gpt-message-header">
                <img src={botIcon} alt="복지봇" className="bot-icon" />
                <span className="bot-name">복지봇</span>
              </div>
            )}
            {message.type === 'user' && (
              <div className="user-message-header">
                <span className="user-name">상담자</span>
                <img src={userIcon} alt="상담자" className="user-icon" />
              </div>
            )}
          <div
            className={`
              ${message.type === 'user' ? 'user-message' : 'gpt-message'} 
              ${message.isTranscription ? 'transcription-message' : ''} 
              ${message.isChatSummary ? 'chat-summary-message' : ''} 
            `}
          >
              {message.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;