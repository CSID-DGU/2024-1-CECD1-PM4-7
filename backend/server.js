// 서버 실행 및 라우팅 작업 수행
require("dotenv").config(); // 환경 변수 로드
const {callUser} = require("./callUser");
const {getGPTResponse} = require("./gpt");
const {streamSTT} = require("./stt");
const {streamTTS} = require("./tts");
const https = require('https');
const fs = require('fs');
const express = require("express");
const WebSocket = require('ws');
const twilio = require("twilio");

const app = express();
const VoiceResponse = twilio.twiml.VoiceResponse;

app.use(express.json()); // JSON 자동 파싱
app.use(express.urlencoded({extended: true})); // URL 자동 파싱

// SSL 인증서와 개인 키 읽기
const options = {
  cert: fs.readFileSync('/etc/letsencrypt/live/welfarebot.kr/fullchain.pem'),
  key: fs.readFileSync('/etc/letsencrypt/live/welfarebot.kr/privkey.pem'),
};

// HTTPS 서버 및 WebSocket 설정
const httpsServer = https.createServer(options, app);
const wss = new WebSocket.Server({server: httpsServer});

let isFirstCalling = true; // 중복 전화 방지 플래그

// HTTPS 포트 443에서 서버 리스닝
httpsServer.listen(443, () => {
  console.log("HTTPS 서버가 포트 443에서 실행 중입니다.");
});

// HTTP 포트 80을 열어 HTTPS로 리디렉션하는 옵션
const http = require('http');
http.createServer(app).listen(80, () => {
  console.log("HTTP 서버가 포트 80에서 실행 중입니다. HTTPS로 리디렉션합니다.");
});

// 사용자에게 전화를 걸음
app.get("/call", async (req, res) => {
  if (!isFirstCalling) {
    return res.status(429).send("이미 전화가 진행 중입니다.");
  }

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
    // 사용자 인증 메시지 출력
    // twiml.say({language: "ko-KR"}, message);
    // console.log("사용자 인증 메시지: ", message);

    // 상담 시작 메시지 출력
    const gptResponse = await getGPTResponse(gptRequest);

    twiml.say({language: "ko-KR"}, gptResponse);
    console.log("상담 시작 메시지: ", gptResponse);

    //양방향 스트림 연결 설정
    const connect = twiml.connect();
    connect.stream({
      url: 'wss://welfarebot.kr',
      name: 'conversation_stream'
    });
  } catch (error) {
    console.error("GPT 응답 처리 중 오류 발생: ", error);
  }

  res.type("text/xml");
  res.send(twiml.toString());
});

// WebSocket 연결
wss.on('connection', (ws) => {
  console.log("WebSocket 연결 성공");
  ws.on('message', (audioData) => {
    // 실시간 STT 처리
    streamSTT(audioData, async (transcription) => {
      console.log("STT 결과: ", transcription);

      // STT 결과를 GPT에 전달
      const gptResponse = await getGPTResponse(transcription);
      console.log("GPT 결과: ", gptResponse);

      // GPT 응답을 TTS로 변환
      const ttsAudio = await streamTTS(gptResponse);

      // Twlio에 TTS 음성 데이터 전송
      ws.send(ttsAudio);
      console.log("음성 데이터 전송 완료.");
    });
  });

  // 연결 종료 처리
  ws.on('close', () => {
    console.log("클라이언트와 연결이 종료되었습니다.");
  });
});

