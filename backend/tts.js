// 구글 TTS로 텍스트를 음성으로 변환
const {TextToSpeechClient} = require('@google-cloud/text-to-speech');
const {PassThrough} = require('stream');

const client = new TextToSpeechClient({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
});

async function sendTTSResponse(ws, streamSid, gptResponse){
  const speechStream = await synthesizeSpeechToStream(gptResponse);

  speechStream.on('data', chunk => {
    const payloadWithoutHeader = removeHeaderBytes(chunk);
    const base64Payload = payloadWithoutHeader.toString('base64');
    // console.log("Base64 인코딩된 데이터:", base64Payload.slice(0, 100));
    ws.send(
      JSON.stringify({
        event: 'media',
        streamSid: streamSid,
        media: {
          payload: base64Payload,
        }
      })
    );
  });

  speechStream.on('error', console.error);

  speechStream.on('end', () => {
    // 음성 출력이 완료되면 종료를 알리는 mark 메시지 전송
    ws.send(
      JSON.stringify({
        event: 'mark',
        streamSid: streamSid,
        mark: {
          name: 'TTS-end'
        }
      })
    );
  });
}

/**
 * GPT로부터 받은 텍스트를 음성으로 변환하고, 음성 데이터를 스트림으로 전송하는 함수
 * @param {string} gptResponse - 변환할 텍스트
*/
async function synthesizeSpeechToStream(gptResponse) {
  const request = {
    input: { text: gptResponse },
    voice: { languageCode: 'ko-KR', ssmlGender: 'NEUTRAL' },
    audioConfig: { 
      audioEncoding: 'MULAW',
      sampleRateHertz: 8000,
     },
  };

  const [response] = await client.synthesizeSpeech(request);

  const speechStream = new PassThrough();
  speechStream.end(response.audioContent);

  return speechStream;
}

function removeHeaderBytes(chunk) {
  const headerSize = 44;  //62
  return chunk.slice(headerSize);
}

module.exports = {sendTTSResponse};
