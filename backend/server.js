// 서버 실행 및 라우팅 작업 수행
require("dotenv").config(); // 환경 변수 로드
const {getPhoneNumbers, getCrisisTypes, updateCrisisTypes, callUser} = require("./dynamoDB.js");
const {createRecognizeStream} = require('./stt');
const {sendTTSResponse} = require("./tts");
const {playBeepSound} = require("./playBeepSound.js");
const {getSttEvaluationModelResponse} = require("./sttEvaluationModel");
const {getSttCorrectionModelResponse, resetSttCorrectionModelConversations} = require("./sttCorrectionModel");
const {getChatModelResponse, resetChatModelConversations} = require("./chatModel");
const {getChatSummaryModelResponse, resetChatSummaryModelConversations} = require("./chatSummaryModel");
const {saveDataToSpreadsheets} = require('./spreadsheet');
const https = require('https');
const fs = require('fs');
const path = require('path');
const express = require("express");
const WebSocket = require('ws');
const twilio = require("twilio");

const app = express();

// 테스트

// JSON과 URL 자동 파싱
app.use(express.json()); 
app.use(express.urlencoded({extended: true}));

// React 정적 파일 제공
app.use(express.static(path.join(__dirname, '../frontend/build')));

// SSL 인증서와 개인 키 읽기
const options = {
  cert: fs.readFileSync('/etc/letsencrypt/live/welfarebot.kr/fullchain.pem'),
  key: fs.readFileSync('/etc/letsencrypt/live/welfarebot.kr/privkey.pem'),
};

// HTTPS 서버 및 WebSocket 설정
const httpsServer = https.createServer(options, app);
const wss = new WebSocket.Server({noServer:true}); // WebSocket 서버 하나로 통합

// HTTPS 포트 443에서 서버 리스닝
httpsServer.listen(443, () => {
  console.log("HTTPS 서버가 포트 443에서 실행 중입니다.");
});

// HTTP 포트 80을 열어 HTTPS로 리디렉션하는 옵션
const http = require('http');
http.createServer(app).listen(80, () => {
  console.log("HTTP 서버가 포트 80에서 실행 중입니다. HTTPS로 리디렉션합니다.");
});

// 전화 번호 목록 가져오기
app.get('/api/getPhoneNumbers', async (req, res) => {
  try {
    const phoneNumbers = await getPhoneNumbers();
    res.json(phoneNumbers);
  } catch (error) {
    console.error("전화번호 목록 불러오기 오류:", error);
    res.status(500).send("오류 발생");  
  }
});

// 위기 유형 가져오기
app.get('/api/getCrisisTypes', async (req, res) => {
  const phoneNumber = decodeURIComponent(req.query.phoneNumber);
  try {
    const crisisTypes = await getCrisisTypes(phoneNumber);
    res.json(crisisTypes);
  } catch (error) {
    console.error('위기 유형 가져오기 오류:', error);
    res.status(500).send('오류 발생');
  }
});

// 위기 유형 업데이트
app.post('/api/updateCrisisTypes', async (req, res) => {
  const { phoneNumber, crisisTypes } = req.body;
  try {
    await updateCrisisTypes(phoneNumber, crisisTypes);
    console.log('위기 유형 업데이트 성공');
    res.status(200).send('위기 유형 업데이트 성공');
  } catch (error) {
    console.error('위기 유형 업데이트 오류:', error);
    res.status(500).send('위기 유형 업데이트 실패');
  }
});

// 현재 진행 중인 전화 상태 저장
const activeCalls = new Map();

// 전화 요청
app.get("/call", async (req, res) => {
  const { phoneNumber } = req.query;

  // 이미 해당 번호로 전화가 진행 중인지 확인
  if (activeCalls.has(phoneNumber)) {
    console.log("\n", phoneNumber, "는 이미 통화가 진행 중입니다");
    return res.status(429).send(`${phoneNumber}는 이미 통화가 진행 중입니다.`);
  }

  // 전화 진행 중인 상태로 설정
  activeCalls.set(phoneNumber, true);

  // 전화 걸기
  try {
    await callUser(phoneNumber);
    console.log("\n", phoneNumber, "로 전화가 성공적으로 걸렸습니다");
    res.status(200).send('전화가 성공적으로 걸렸습니다.');
  } catch (error) {
    // 오류 발생 시 전화 상태 초기화
    activeCalls.delete(phoneNumber);
    console.error("\n", phoneNumber, "로 전화 거는 중 오류 발생:", error);
    res.status(500).send(`${phoneNumber}로 전화 거는 중 오류 발생`);
  } 
});


// 통화 연결
app.post("/voice", async (req, res) => {
  const VoiceResponse = twilio.twiml.VoiceResponse;
  const twiml = new VoiceResponse();
  const gptRequest = req.query.gptRequest;
  const phoneNumber = req.query.phoneNumber;

  try {    
    // 양방향 스트림 연결 설정
    const connect = twiml.connect();
    const stream = connect.stream({
      url: 'wss://welfarebot.kr/twilio',
      name: 'conversation_stream'
    });

    // 파라미터 추가
    stream.parameter({
      name: 'gptRequest',
      value: gptRequest
    });
    stream.parameter({
      name: 'phoneNumber',
      value: phoneNumber
    });

  } catch (error) {
    console.error("오류 발생: ", error);
  }

  res.type("text/xml");
  res.send(twiml.toString());
});

// API 경로 외의 모든 요청을 index.html로 라우팅
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/build', 'index.html'));
});


// React WebSocket 연결을 전역 변수로 저장
let wsReactConnections = new Map();

// 업그레이드 요청 처리
httpsServer.on('upgrade', (request, socket, head) => {
  const url = new URL(request.url, `https://${request.headers.host}`);
  const pathname = url.pathname;
  const searchParams = url.searchParams;

  // 리엑트 WebSocket
  if (pathname === '/react') {
    wss.handleUpgrade(request, socket, head, (wsReact) => {
      console.log("\nReact WebSocket 연결 성공");
      const phoneNumber = searchParams.get('phoneNumber');

      wsReactConnections.set(phoneNumber, wsReact); // 전화 번호를 키로 저장

      wsReact.on('close', () => {
        console.log(`React WebSocket 연결 종료 (전화번호: ${phoneNumber})`);
        wsReactConnections.delete(phoneNumber); // React 연결 종료 시 제거
      });
    });
  } 

  // twilio WebSocket
  else if (pathname === '/twilio') {
    wss.handleUpgrade(request, socket, head, (wsTwilio) => {
      let wsReactConnection = null;
      let recognizeStream = null;
      let timeoutHandle = null;
      let isAudioProcessing = true;
      let chatModelResponse = null;
      let phoneNumber = null;

      wsTwilio.on('message', message => {
        const msg = JSON.parse(message);

        switch (msg.event) {
          case "connected":
            break;
          case "start":
            phoneNumber = msg.start.customParameters.phoneNumber;
            const gptRequest = msg.start.customParameters.gptRequest;
            console.log("\n전화번호", phoneNumber);
            
            // 상담 시작 메시지 출력
            (async() => {
              try {
                chatModelResponse = await getChatModelResponse(phoneNumber, gptRequest);
                await sendTTSResponse(wsTwilio, msg.streamSid, chatModelResponse);
                console.log("\n복지봇: ", chatModelResponse);

                // 해당 전화번호의 React WebSocket으로도 대화 전송
                wsReactConnection = wsReactConnections.get(phoneNumber);
                if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
                  wsReactConnection.send(JSON.stringify({ event: 'gptResponse', chatModelResponse }));
                }
              } catch(error){
                console.error("오류 발생: ", error);
              }
            }) ();    
            break;

          case "media":
            // 사용자 음성을 처리 중일 경우 음성 무시
            if (isAudioProcessing) {
              return;
            }

            if(!recognizeStream) {
              //실시간 음성 처리
              //console.log("새 STT 스트림 생성");

              recognizeStream = createRecognizeStream()
                .on('error', console.error)
                .on('data', data => {
                  const transcription = data.results[0].alternatives[0].transcript;
            
                  // 1초 이내에 다음 전사된 텍스트를 받으면 타이머 초기화
                  if(timeoutHandle) {
                    clearTimeout(timeoutHandle);
                  }
            
                  // 1초 동안 구글 STT로 부터 받은 데이터가 없으면 문장이 끝났다고 판단
                  timeoutHandle = setTimeout(async () => {
                    isAudioProcessing = true;
                    recognizeStream.destroy();
                    console.log("\n상담자: ", transcription);

                    // Twilio WebSocket에서 받은 STT 전사 데이터를 React로 전송
                    if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
                      wsReactConnection.send(JSON.stringify({ event: 'transcription', transcription }));
                    }

                    // STT 결과를 STT 평가 모델에 전달
                    const sttEvaluationModelResponse = await getSttEvaluationModelResponse(chatModelResponse, transcription);
                    console.log("상담자(STT 평가 결과): ", sttEvaluationModelResponse);
                    if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
                      wsReactConnection.send(JSON.stringify({ event: 'sttEvaluation', sttEvaluationModelResponse }));
                    }

                    // STT 평가 결과에 따라 처리 
                    switch (sttEvaluationModelResponse) {
                      // 통과일 경우 STT 전사 결과를 대화 진행 모델에 전달
                      case '통과':
                        chatModelResponse = await getChatModelResponse(phoneNumber, transcription);
                        break;

                      // 완전 손상일 경우 완전손상 메세지를 대화 진행 모델에 전달
                      case '완전손상':
                        chatModelResponse = await getChatModelResponse(phoneNumber, sttEvaluationModelResponse);
                        break;

                      // 불충분일 경우 STT 전사 결과를 STT 교정모델에 전달한 후, 교정 결과를 대화 진행 모델에 전달 
                      case '불충분':
                        const sttCorrectionModelResponse = await getSttCorrectionModelResponse(phoneNumber, chatModelResponse, transcription);
                        console.log("상담자(STT 교정 결과): ", sttCorrectionModelResponse);
                        if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
                          wsReactConnection.send(JSON.stringify({ event: 'sttCorrection', sttCorrectionModelResponse }));
                        }
                        chatModelResponse = await getChatModelResponse(phoneNumber, sttCorrectionModelResponse);
                        break;

                      default:
                        console.error("알 수 없는 평가 결과: ", sttEvaluationModelResponse);
                    }

                    console.log("\n복지봇: ", chatModelResponse, "\n");
                    if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
                      wsReactConnection.send(JSON.stringify({ event: 'gptResponse', chatModelResponse }));
                    }

                    // GPT 응답을 TTS로 변환
                    await sendTTSResponse(wsTwilio, msg.streamSid, chatModelResponse);
                  }, 1000);
                });
            }

            // 스트림이 존재하고 destroy 되지 않았을 때 스트림에 데이터 쓰기
            if(!recognizeStream.destroyed && recognizeStream) {
              recognizeStream.write(msg.media.payload);
            }
            break;

          case "mark":          
            playBeepSound(wsTwilio, msg.streamSid);  //삐 소리 출력
            isAudioProcessing = false;
            recognizeStream = null;
            break;
          
          // 전화가 종료됐을 때: 대화 내용 요약, 스프레드 시트에 대화 내역 저장, 사용자 정보 초기화
          case "stop":
            console.log("\n전화 종료");
            
            (async () => {
              const chatSummaryModelResponse = await getChatSummaryModelResponse(phoneNumber);
              console.log("\n대화 내용 요약:", chatSummaryModelResponse);
              if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
                wsReactConnection.send(JSON.stringify({ event: 'chatSummary', chatSummaryModelResponse }));
              }

              // 스프레드 시트에 대화 내역 저장
              try {
                await saveDataToSpreadsheets(phoneNumber);
                wsReactConnection.send(JSON.stringify({ event: 'toast', message: '상담 데이터가 스프레드시트에 성공적으로 저장되었습니다!' }));
              } catch(error) {
                console.error("스프레드 시트에 데이터 저장 중 오류 발생: ", error);
              }

              // 각 모델의 대화 기록 초기화
              resetChatModelConversations(phoneNumber);
              resetSttCorrectionModelConversations(phoneNumber);
              resetChatSummaryModelConversations(phoneNumber);

              // STT 스트림 초기화
              if (recognizeStream) {
                recognizeStream.destroy(); // STT 스트림 종료
                recognizeStream = null; // STT 스트림을 null로 설정
              }
              
              // 전화 연결 상태 및 음성 처리 상태 초기화
              isAudioProcessing = false;
              
              // 타이머 및 기타 상태 초기화
              if (timeoutHandle) {
                clearTimeout(timeoutHandle);
                timeoutHandle = null; // 타이머 초기화
              }              

              // 전화 상태 초기화
              activeCalls.delete(phoneNumber);
              console.log(`\n대화 내용 저장 및 사용자 정보 초기화 완료(사용자: ${phoneNumber})`);
            }) ();
            break;
        }
      });
    });
  } 
  else {
    socket.destroy(); // 다른 경로는 연결 종료
  }
});