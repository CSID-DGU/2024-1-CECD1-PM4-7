import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { ToastContainer, toast } from 'react-toastify';  // Toast 컴포넌트 임포트
import 'react-toastify/dist/ReactToastify.css';  // Toast 스타일 임포트
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
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  
  const chatContainerRef = useRef(null);

  useEffect(() => {
    // DynamoDB에서 이름 목록 가져오기
    fetch('/api/getPhoneNumbers')
      .then(response => response.json())
      .then(data => setPhoneNumbers(data))
      .catch(error => console.error('전화번호 불러오기 오류:', error));
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

  // "전화 걸기" 버튼 클릭 시 처리
  const handleCallClick = async () => {
    if (!selectedPhoneNumber) {
      alert('전화번호를 선택해주세요.');
      return;
    }

    // 위기 유형이 최소 하나는 선택되어야 함
    const selectedCrisisTypes = crisisTypes.filter(type => type);
    if (selectedCrisisTypes.length === 0) {
      alert('적어도 하나의 위기 유형을 선택해주세요.');
      return;
    }

    try {
      // 서버로 업데이트 요청 보내기
      const response = await fetch('/api/updateCrisisTypes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phoneNumber: selectedPhoneNumber,
          crisisTypes: selectedCrisisTypes,
        }),
      });

      if (response.ok) {
        // 전화 걸기 API 호출
        const callResponse = await fetch(`/call?phoneNumber=${encodeURIComponent(selectedPhoneNumber)}`);
        if (callResponse.ok) {
          alert('전화 연결이 시작되었습니다.');
          setMessages([]); // 대화 초기화

          const socket = new WebSocket(`wss://welfarebot.kr/react?phoneNumber=${encodeURIComponent(selectedPhoneNumber)}`);
          
          socket.onopen = () => {
            console.log('WebSocket 연결 성공');
          };

          socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
          
            switch (data.event) {
              case 'transcription':
                setMessages((prevMessages) => [
                  ...prevMessages,
                  { type: 'user', text: `원문: ${data.transcription}`, isTranscription: true },
                ]);
                break;
          
              case 'sttEvaluation':
                setMessages((prevMessages) => [
                  ...prevMessages,
                  { type: 'user', text: `STT 평가 결과: ${data.sttEvaluationModelResponse}`, isTranscription: false },
                ]);
                break;
          
              case 'sttCorrection':
                setMessages((prevMessages) => [
                  ...prevMessages,
                  { type: 'user', text: `STT 교정 결과: ${data.sttCorrectionModelResponse}`, isTranscription: false },
                ]);
                break;
          
              case 'gptResponse':
                setMessages((prevMessages) => [
                  ...prevMessages,
                  { type: 'gpt', text: data.chatModelResponse, isChatSummary: false },
                ]);
                break;
          
              case 'chatSummary':
                setMessages((prevMessages) => [
                  ...prevMessages,
                  { type: 'gpt', text: `대화 내용 요약: ${data.chatSummaryModelResponse}`, isChatSummary: true },
                ]);
                break;
          
              case 'toast':
                toast.success(data.message);
                break;
          
              default:
                console.warn('알 수 없는 이벤트 타입:', data.event);
            }
          };
      
          socket.onclose = () => {
            console.log('React WebSocket 연결 종료');
          };
        } 
      } 
    } catch (error) {
      console.error('DB 업데이트 및 전화거는 과정에서 오류 발생:', error);
      alert('오류가 발생했습니다.');
    }
  };

  // 컴포넌트 언마운트 시 WebSocket 연결 해제
  useEffect(() => {
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [socket]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]); // messages가 변경될 때마다 실행

  return (
    <div>
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

        <div className="date">2024.10.18</div>

        <div className="chat-container" ref={chatContainerRef}>
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
                  ${message.colorClass || ''}
  `             }
              >
                {message.text}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className = "dropdown-container">
        <div className="dropdown-row">
          <label>전화번호: </label>
          <select value={selectedPhoneNumber} onChange={handlePhoneNumberChange}>
            <option value="">전화번호 선택</option>
            {phoneNumbers.map((phoneNumber) => (
              <option key={phoneNumber} value={phoneNumber}>{phoneNumber}</option>
            ))}
        </select>
        </div>

        {[0, 1, 2].map((index) => (
          <div className="dropdown-row" key={index}>
            <label>위기 유형 {index + 1}: </label>
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
        <div className="dropdown-row">
          <button onClick={handleCallClick}>전화 걸기</button>
        </div>
      </div>

      <ToastContainer position="top-center" autoClose={2500} hideProgressBar={false} closeOnClick />
    </div>
  );
}

export default App;