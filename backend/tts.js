// 구글 TTS로 텍스트를 음성으로 변환
const {TextToSpeechClient} = require('@google-cloud/text-to-speech');
const {Writable} = require('stream');
const client = new TextToSpeechClient({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
});

/**
 * GPT로부터 받은 텍스트를 음성으로 변환하고, 음성 데이터를 스트림으로 전송하는 함수
 * @param {string} text - 변환할 텍스트
 * @param {function} onAudioData - 생성된 음성 데이터를 처리하는 콜백 함수
 */
async function streamTTS(text, onAudioData) {
  const request = {
    input: { text: text },
    voice: { languageCode: 'ko-KR', ssmlGender: 'NEUTRAL' },
    audioConfig: { audioEncoding: 'LINEAR16' },
  };

  const [response] = await client.synthesizeSpeech(request);

  const audioStream = new Writable({
    write(chunk, encoding, callback) {
      onAudioData(chunk);
      callback();
    },
  });

  audioStream.end(response.audioContent);
}

module.exports = { streamTTS };
