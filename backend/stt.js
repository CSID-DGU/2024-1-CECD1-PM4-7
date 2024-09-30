// 구글 STT로 음성을 텍스트로 변환
const {SpeechClient} = require("@google-cloud/speech");
const client = new SpeechClient({
  keyFilename: process.env.GOOGLE_APPICATION_CREDENTIALS,
});

/**
 * 음성 데이터를 받아서 텍스트로 변환하는 함수
 * @param {string} decodedAudio - 음성 데이터
 * @param {string} onTranscription - 전사된 텍스트
 */
async function streamSTT(decodedAudio, onTranscription) {
  console.log("streamSTT 호출");
  // 음성 파일 요구 사항
  const request = {
    config: {
      encoding: "MULAW",  // LINEAR16
      sampleRateHertz: 8000,
      languageCode: "ko-KR",
    },
    interimResults: false, // 최종 결과만 저장
  };
  
  //실시간 음성 처리 기능
  const recognizeStream = client
    .streamingRecognize(request)
    .on('error', console.error)
    .on('data', (data) => {
      // VAD가 자동으로 음성 종료를 감지했을 때 결과 전송
      console.log("음성 데이터 수신");
      if (data.results[0] && data.results[0].isFinal) {
        const transcription = data.results[0].alternatives[0].transcript;
        console.log("STT 전사 결과: ", transcription);
        onTranscription(transcription);
      }
    });

    // 실시간 음성 데이터를 Google STT로 스트리밍
    console.log("STT 스트리밍 시작");
    recognizeStream.write(decodedAudio);
    // recognizeStream.end();
}

module.exports = {streamSTT};
