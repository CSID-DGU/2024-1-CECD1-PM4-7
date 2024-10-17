import React, { useState, useEffect } from 'react';
import './App.css';
import botIcon from './logo_black.png';
import userIcon from './user.png';

const crisisOptions = [
  "요금 체납", "주거 위기", "고용위기", 
  "급여/서비스 탈락", "긴급상황 위기", "건강 위기", "에너지 위기"
];

function App() {
  const [phoneNumbers, setPhoneNumbers] = useState([]);  // 전화번호 리스트
  const [selectedPhoneNumber, setSelectedPhoneNumber] = useState('');
  const [crisisTypes, setCrisisTypes] = useState(['', '', '']); // 위기 유형
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // DynamoDB에서 이름 목록 가져오기
    fetch('/api/getPhoneNumbers')
      .then(response => response.json())
      .then(data => setPhoneNumbers(data))
      .catch(error => console.error('이름 불러오기 오류:', error));
  }, []);

  // 이름 선택 시 위기 유형 가져오기
  const handlePhoneNumberChange = async (event) => {
    const selected = event.target.value;
    setSelectedPhoneNumber(selected);

    // 선택한 사용자의 위기 유형 가져오기
    try {
      const response = await fetch(`/api/getCrisisTypes?phoneNumber=${encodeURIComponent(selected)}`);
      const data = await response.json();
      setCrisisTypes([...data, '', ''].slice(0, 3)); // 최대 3개만 설정
    } catch (error) {
      console.error('위기 유형 가져오기 오류:', error);
    }
  };

  const handleCrisisChange = (index, value) => {
    const newCrisisTypes = [...crisisTypes];
    newCrisisTypes[index] = value;
    setCrisisTypes(newCrisisTypes);
  };

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

    <div>
      <label>전화번호:</label>
      <select value={selectedPhoneNumber} onChange={handlePhoneNumberChange}>
        <option value="">전화번호 선택</option>
        {phoneNumbers.map((phoneNumber) => (
          <option key={phoneNumber} value={phoneNumber}>{phoneNumber}</option>
        ))}
      </select>

      {[0, 1, 2].map((index) => (
        <div key={index}>
          <label>위기 유형 {index + 1}:</label>
          <select
            value={crisisTypes[index]}
            onChange={(e) => handleCrisisChange(index, e.target.value)}
          >
            <option value="">선택</option>
            {crisisOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
      ))}
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