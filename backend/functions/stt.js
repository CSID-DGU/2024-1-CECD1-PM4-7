// 구글 STT로 음성을 텍스트로 변환
const axios = require("axios");
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const {SpeechClient} = require("@google-cloud/speech");
const speechClient = new SpeechClient({
  keyFilename: process.env.GOOGLE_APPICATION_CREDENTIALS,
});

/**
 * Twilio에서 녹음 파일을 다운로드하는 함수
 * @param {string} url - 녹음 파일의 URL
 * @return {Promise<{status: number, data: Buffer}>} - HTTP 응답 상태와 다운로드된 녹음 데이터
 */
async function downloadRecording(url) {
  try {
    const response = await axios({
      url: url,
      method: "GET",
      responseType: "arraybuffer", // 버퍼로 응답 받기
      headers: {
        "Authorization": `Basic ${Buffer
            .from(`${accountSid}:${authToken}`)
            .toString("base64")}`,
      },
    });

    const buffer = Buffer.from(response.data);
    console.log(`녹음 파일 크기: ${buffer.length}`);
    return {status: response.status, data: buffer};
  } catch (error) {
    if (error.response && error.response.status === 404) {
      console.log("녹음 파일이 아직 준비되지 않았을 수 있습니다.");
      return {status: 404};
    } else {
      console.error("녹음 파일 다운로드 중 오류 발생1:", error);
      throw error;
    }
  }
}

/**
 * 음성 데이터를 받아서 텍스트로 변환하는 함수
 * @param {string} audioBuffer - 음성 데이터
 * @return {Promise<string>} 변환된 텍스트
 */
async function transcribeAudio(audioBuffer) {
  const audio = {
    content: audioBuffer.toString("base64"),
  };

  // 음성 파일 요구 사항
  const request = {
    audio: audio,
    config: {
      encoding: "LINEAR16",
      sampleRateHertz: 8000,
      languageCode: "ko-KR",
    },
  };

  // 요청된 STT 결과 처리
  const [response] = await speechClient.recognize(request);
  const transcription = response.results
      .map((result) => result.alternatives[0].transcript)
      .join("\n");

  console.log("전사된 사용자 응답1: ", transcription); // 전사된 텍스트를 로그로 출력

  return transcription;
}

module.exports = {downloadRecording, transcribeAudio};
