// STT 오류 교정 모델
const { callOpenAI } = require("./openaiClient");
const { promptData, modelData } = require("./configLoader");

// 프롬프트, 모델명, 토큰 수 설정
const Prompt = promptData.stt_correction_241015;
const modelName = modelData.stt_correction;
const maxTokens = 256;

// 각 사용자의 대화 기록을 저장
const allConversationsMap = new Map();

// STT로 전사된 텍스트를 GPT API에 전달하고 응답을 처리하는 함수
async function getSttCorrectionModelResponse(phoneNumber, gptInquiry, transcription) {
  // gpt 응답을 바탕으로 프롬프트 재구성
  const modifiedPrompt = Prompt
    .replace("{}", `"${gptInquiry}"`)
    .replace("{}", `"${transcription}"`);

  // GPT API에 보낼 메세지 구성
  const conversations = [
    { role: "system", content: modifiedPrompt },
    { role: "user", content: transcription },
  ];

  // STT 교정 결과
  const correctionResult = await callOpenAI(modelName, conversations, maxTokens);

  // 현재 대화 내용을 전체 대화 내용에 추가
  conversations.push({ role: "assistant", content: correctionResult });
  let userConversations = allConversationsMap.get(phoneNumber) || [];
  userConversations.push(conversations);
  allConversationsMap.set(phoneNumber, userConversations);

  // console.log("stt 교정 모델 로그: ", allConversationsMap.get(phoneNumber));
  return correctionResult;
}

// 대화 기록 초기화
function resetSttCorrectionModelConversations(phoneNumber) {
  allConversationsMap.delete(phoneNumber);
}

module.exports = {allConversationsMap,getSttCorrectionModelResponse, resetSttCorrectionModelConversations};
