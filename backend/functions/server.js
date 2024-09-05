// 서버 실행 및 라우팅 작업 수행
require("dotenv").config(); // .env 파일에서 환경 변수 로드
const {addUser} = require("./addUser");
const {callUser} = require("./callUser");
const {getGPTResponse} = require("./gpt");
const {downloadRecording, transcribeAudio} = require("./stt");
const twilio = require("twilio");
const express = require("express");
const session = require("express-session");

const VoiceResponse = twilio.twiml.VoiceResponse;

let isFirstCalling = true; // 중복 전화 방지 플래그

const app = express();

app.use(express.json()); // JSON 자동 파싱
app.use(express.urlencoded({extended: true})); // URL 자동 파싱

app.use(session({
  secret: process.env.SESSION_SECRET_KEY,
  resave: false,
  saveUninitialized: false,
  cookie: {secure: false},
}));

// 파이어스토어에 사용자 정보 저장
app.post("/addUser", async (req, res) => {
  const {name, phoneNumber, crisisTypes} = req.body;
  await addUser(name, phoneNumber, crisisTypes);
  res.status(200).send("사용자 정보가 성공적으로 저장됨");
});

// 사용자에게 전화를 걸음
app.get("/call", async (req, res) => {
  if (!isFirstCalling) {
    return res.status(429).send("이미 전화가 진행 중입니다.");
  }

  isFirstCalling = true;

  try {
    await callUser();
    res.status(200).send("전화가 성공적으로 걸림");
  } catch (error) {
    console.error("전화 거는 과정에서 오류 발생: ", error);
  }
});

// 전화 관련 작업 처리
app.post("/voice", async (req, res) => {
  const twiml = new VoiceResponse();
  // 초기 메시지 출력
  try {
    // const message = req.query.message;
    const gptRequest = req.query.gptRequest;

    // 사용자 인증 메시지 출력
    // twiml.say({language: "ko-KR"}, message);
    // console.log("사용자 인증 메시지: ", message);

    // 상담 시작 메시지 출력
    const clientId = req.session.id;
    const gptResponse = await getGPTResponse(clientId, gptRequest);

    // gptResponse에서 content 부분만 추출
    const gptContent = gptResponse.content;

    twiml.say({language: "ko-KR"}, gptContent);
    console.log("상담 시작 메시지: ", gptContent);
  } catch (error) {
    console.error("GPT 응답 처리 중 오류 발생: ", error);
  }

  console.log("녹음 시작");
  twiml.record({
    action: "/app/recording-complete", // 녹음이 끝난 후 호출되는 웹훅
    method: "POST",
    timeout: 1, // 사용자 응답을 기다리는 시간
    transcribe: false,
  });

  res.type("text/xml");
  res.send(twiml.toString());
});

app.post("/recording-complete", async (req, res) => {
  // twilio에서 전송된 녹음 파일 URL
  const recordingUrl = req.body.RecordingUrl;
  console.log("녹음 파일 URL:", recordingUrl);

  /**
   * 녹음 파일 다운로드, STT, GPT 처리를 수행하는 함수
   * @async
   * @function processRecording
   * @return {Promise<void>} - 함수가 완료될 때까지 기다림
   */
  async function processRecording() {
    try {
      // 녹음 파일 다운로드
      const {status, data: recordingData} =
      await downloadRecording(recordingUrl);

      console.log(`HTTP 상태 코드: ${status}`);

      // 녹음 파일이 다운로드 가능한 경우에만 파일 처리
      if (status === 200) {
        clearInterval(checkRecordingInterval); // 파일이 성공적으로 다운로드되면 반복 중지
        console.log(`녹음 파일 다운로드 성공 - HTTP 상태 코드: ${status}`);

        // Google STT를 사용해 녹음 파일을 전사
        const transcription = await transcribeAudio(recordingData);
        console.log("전사된 사용자 응답2: ", transcription);

        // 전사된 텍스트를 GPT에 입력
        const clientId = req.session.id;
        const gptResponse = await getGPTResponse(clientId, transcription);
        const gptContent = gptResponse.content;
        console.log("GPT 응답: ", gptContent);

        // GPT 응답 음성 출력
        const twiml = new VoiceResponse();
        twiml.say({language: "ko-KR"}, gptContent);

        twiml.record({
          action: "/app/recording-complete", // 녹음 완료 후 다시 이 엔드포인트 호출
          method: "POST",
          timeout: 1, // 사용자 응답을 기다리는 시간
          transcribe: false,
        });

        res.type("text/xml");
        res.send(twiml.toString());
      } else if (status === 404) {
        // 파일이 아직 저장되지 않은 경우 처리
        console.log("녹음 파일이 아직 저장되지 않았습니다. 다시 시도 중...");
      } else {
        console.log(`녹음 파일 다운로드 실패 - HTTP 상태 코드: ${status}`);
      }
    } catch (error) {
      clearInterval(checkRecordingInterval); // 오류 발생 시 반복 중지
      console.log("녹음 파일 다운로드 중 오류 발생2:", error.message);
    }
  }

  // 0.2초마다 녹음 파일이 준비되었는지 확인
  const checkRecordingInterval = setInterval(processRecording, 200);
});

module.exports = app;
