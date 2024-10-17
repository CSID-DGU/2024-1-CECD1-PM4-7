// 서버 실행 및 라우팅 작업 수행
require("dotenv").config(); // 환경 변수 로드
const {callUser} = require("./callUser");
const {createRecognizeStream} = require('./stt');
const {sendTTSResponse} = require("./tts");
const {playBeepSound} = require("./playBeepSound.js");
const {getSttCorrectionModelResponse, resetSttCorrectionModelConversations} = require("./sttCorrectionModel");
const {getChatModelResponse, resetChatModelConversations} = require("./chatModel");
const {getChatSummaryModelResponse, resetChatSummaryModelConversations} = require("./chatSummaryModel");
const https = require('https');
const fs = require('fs');
const path = require('path');
const express = require("express");
const WebSocket = require('ws');
const {parse} = require('url');
const twilio = require("twilio");

const app = express();

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

const VoiceResponse = twilio.twiml.VoiceResponse;
let isFirstCalling = true; // 중복 전화 방지 플래그

// 사용자에게 전화를 걸음
app.get("/call", async (req, res) => {
  if (!isFirstCalling) {
    return res.status(429).send("이미 전화가 진행 중입니다.");
  }

  isFirstCalling = false;

  try {
    await callUser();
    res.status(200).send("전화가 성공적으로 걸림");
  } catch (error) {
    console.error("전화 거는 과정에서 오류 발생: ", error);
  }
});

app.post("/voice", async (req, res) => {
  const twiml = new VoiceResponse();
  const gptRequest = req.query.gptRequest;

  try {    
    //양방향 스트림 연결 설정
    const connect = twiml.connect();
    const stream = connect.stream({
      url: `wss://welfarebot.kr/twilio?gptRequest=${encodeURIComponent(gptRequest)}`,
      name: 'conversation_stream'
    });

    // TwiML에 파라미터 추가
    stream.parameter({
      name: 'gptRequest',
      value: gptRequest
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
let wsReactConnection = null;

// 업그레이드 요청 처리
httpsServer.on('upgrade', (request, socket, head) => {
  const pathname = new URL(request.url, `https://${request.headers.host}`).pathname;

  if (pathname === '/react') {
    wss.handleUpgrade(request, socket, head, (wsReact) => {
      console.log("\nReact WebSocket 연결 성공");
      wsReactConnection = wsReact; // React WebSocket 연결 저장

      wsReact.on('message', (message) => {
        console.log('React WebSocket 메시지: ', message);
      });

      wsReact.on('close', () => {
        console.log('React WebSocket 연결 종료');
        wsReactConnection = null; // React 연결 종료 시 null로 설정
      });
    });
  } 

  else if (pathname === '/twilio') {
    wss.handleUpgrade(request, socket, head, (wsTwilio) => {
      let recognizeStream = null;
      let timeoutHandle = null;
      let isAudioProcessing = true;
      let chatModelResponse = null;

      wsTwilio.on('message', message => {
        const msg = JSON.parse(message);

        switch (msg.event) {
          case "connected":
            break;
          case "start":
            // 상담 시작 메시지 출력
            (async() => {
              try {
                const gptRequest = msg.start.customParameters.gptRequest;
                console.log("gptRequest 값:", gptRequest);
                console.log("gptRequest 형식:", typeof gptRequest);
                chatModelResponse = await getChatModelResponse(gptRequest);
                await sendTTSResponse(wsTwilio, msg.streamSid, chatModelResponse);
                console.log("\n복지봇: ", chatModelResponse);

                // React WebSocket으로도 대화 전송
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

                    // STT 결과를 STT 교정 모델에 전달
                    const sttCorrectionModelResponse = await getSttCorrectionModelResponse(transcription, chatModelResponse);
                    console.log("상담자(STT 교정 결과): ", sttCorrectionModelResponse);
                    if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
                      wsReactConnection.send(JSON.stringify({ event: 'sttCorrection', sttCorrectionModelResponse }));
                    }

                    // 교정된 STT 결과를 대화 진행 모델에 전달
                    chatModelResponse = await getChatModelResponse(sttCorrectionModelResponse);
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

          case "stop":
            if(recognizeStream) {
              recognizeStream.destroy();
            }
            break;
        }
      });
          
      // 연결 종료 처리
      wsTwilio.on('close', async() => {
          const chatSummaryModelResponse = await getChatSummaryModelResponse();
          console.log("\n대화 내용 요약:", chatSummaryModelResponse);
          if (wsReactConnection && wsReactConnection.readyState === WebSocket.OPEN) {
            wsReactConnection.send(JSON.stringify({ event: 'chatSummary', chatSummaryModelResponse }));
          }

          console.log("\n전화 종료");

          // 전화 연결 상태 및 음성 처리 상태 초기화
          isFirstCalling = true;
          isAudioProcessing = false;

          //각 모델의 대화 기록 초기화
          resetChatModelConversations();
          resetSttCorrectionModelConversations();
          resetChatSummaryModelConversations();

          // STT 스트림 초기화
          if (recognizeStream) {
            recognizeStream.destroy(); // STT 스트림 종료
            recognizeStream = null; // STT 스트림을 null로 설정
          }

           // 타이머 및 기타 상태 초기화
          if (timeoutHandle) {
            clearTimeout(timeoutHandle);
            timeoutHandle = null; // 타이머 초기화
            }

          console.log("\n사용자 변수 초기화 완료");
      });  
    });
  } 
  else {
    socket.destroy(); // 다른 경로는 연결 종료
  }
});