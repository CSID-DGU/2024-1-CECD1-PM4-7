// 구글 STT로 음성을 텍스트로 변환
const {SpeechClient} = require("@google-cloud/speech");
const client = new SpeechClient({
  keyFilename: process.env.GOOGLE_APPICATION_CREDENTIALS,
});

const request = {
  config: {
    encoding: "MULAW",
    sampleRateHertz: 8000,
    languageCode: "ko-KR",
    model: "telephony",
  },
  interimResults: true  // 중간 결과 반환
};

function createRecognizeStream() {
  return client.streamingRecognize(request);
}

module.exports = { createRecognizeStream };