const path = require('path');
const { PassThrough } = require('stream');

// 오디오 파일 경로 설정
const audioFilePath = path.join(__dirname, 'sound', 'beep.wav');

async function playBeepSound(ws, streamSid) {
  // 음성 파일을 읽고 스트림으로 전송
  const audioStream = await convertAudioToMulawStream(audioFilePath);

  audioStream.on('data', chunk => {
    const base64Payload = chunk.toString('base64');
    ws.send(
      JSON.stringify({
        event: 'media',
        streamSid: streamSid,
        media: {
          payload: base64Payload,
        },
      })
    );
  });

  audioStream.on('error', console.error);
}

// 음성 파일을 읽어 mulaw 형식의 오디오 데이터로 변환하고 스트림을 반환
async function convertAudioToMulawStream(audioFilePath) {
  const ffmpeg = require('fluent-ffmpeg');
  const passThroughStream = new PassThrough();

  // ffmpeg를 사용하여 음성 파일을 mulaw/8000 Hz로 변환
  ffmpeg(audioFilePath)
    .audioCodec('pcm_mulaw')
    .audioFrequency(8000)
    .format('mulaw')
    .on('error', (err) => {
      console.error('ffmpeg 변환 중 오류 발생:', err);
    })
    .pipe(passThroughStream);

  return passThroughStream;
}

module.exports = { playBeepSound };
