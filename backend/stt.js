// 구글 STT로 음성을 텍스트로 변환
const {SpeechClient} = require("@google-cloud/speech");
const client = new SpeechClient({
  keyFilename: process.env.GOOGLE_APPICATION_CREDENTIALS,
});

/**
 * 음성 데이터를 받아서 텍스트로 변환하는 함수
 * @param {string} audioBuffer - 음성 데이터
 * @param {string} onTranscription - 전사된 텍스트
 */
async function streamSTT(audioBuffer, onTranscription) {
  // 음성 파일 요구 사항
  const request = {
    config: {
      encoding: "LINEAR16",
      sampleRateHertz: 8000,
      languageCode: "ko-KR",
    },
    interimResults: false, // 최종 결과만 저장
  };
  
  //실시간 음성 처리 기능
  const recognizeStream = client
    .streamingRecognize(request)
    .on('error', (err) => {
      console.error('Google STT Error: ', err);
    })
    .on('data', (data) => {
      if (data.results[0] && data.results[0].isFinal) {
        // VAD가 자동으로 음성 종를 감지했을 때 결과 전송
        const transcription = data.results[0].alternatives[0].transcript;
        onTranscription(transcription);
      }
    });

    // 실시간 음성 데이터를 Google STT로 스트리밍
    recognizeStream.write(audioBuffer);
    recognizeStream.end(); // 데이터를 모두 보냈다는 신호
}

module.exports = {streamSTT};
