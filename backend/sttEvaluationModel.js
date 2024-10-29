// STT 평가 모델
const { callOpenAI } = require("./openaiClient");
const { promptData, modelData } = require("./configLoader");

// 프롬프트, 모델명, 토큰 수 설정
const Prompt = promptData.stt_validation_241021;
const modelName = modelData.stt_validation;
const maxTokens = 256;

// STT로 전사된 텍스트를 평가
async function getSttEvaluationModelResponse(gptInquiry, transcription) {
  // gpt 응답을 바탕으로 프롬프트 재구성
  const modifiedPrompt = Prompt
    .replace("{}", `"${gptInquiry}"`)
    .replace("{}", `"${transcription}"`);

  // GPT API에 보낼 메세지 구성
  const conversations = [
    { role: "system", content: modifiedPrompt },
    { role: "user", content: transcription },
  ];

  // STT 평가 결과
  const evaluationResult = await callOpenAI(modelName, conversations, maxTokens);

  return evaluationResult;
}

module.exports = {getSttEvaluationModelResponse};
