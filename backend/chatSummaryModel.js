// 대화 요약 모델
const { callOpenAI } = require("./openaiClient");
const { promptData, modelData } = require("./configLoader");
const { conversationsMap } = require("./chatModel");

// 프롬프트, 모델명, 토큰 수 설정
const Prompt = promptData.playground_summary;
const modelName = modelData.Summary;
const maxTokens = 1024;

// 각 사용자의 대화 기록을 저장
const allConversationsMap = new Map();

// STT로 전사된 텍스트를 GPT API에 전달하고 응답을 처리하는 함수
async function getChatSummaryModelResponse(phoneNumber) {

  // 대화 요약을 위해 진행된 대화 내용 가져오기
  let contents = conversationsMap.get(phoneNumber) || [];

  // 시스템 메시지를 제외한 사용자와 봇의 대화 내용을 하나의 문자열로 합침
  const mergedContent = contents
    .slice(1)  // 첫 번째 시스템 메시지 제외
    .map(item => `${item.role}: ${item.content}`)  // role과 content를 조합
    .join('\n');  // 줄바꿈으로 병합
  
  // 요약 모델 프롬프트와 대화 기록
  const conversations = [
    { role: "system", content: Prompt },
    { role: "user", content: mergedContent },
  ];

  // GPT API 호출
  const gptContent = await callOpenAI(modelName, conversations, maxTokens);

  // 현재 대화 내용을 전체 대화 내용에 추가
  conversations.push({ role: "assistant", content: gptContent });
  allConversationsMap.set(phoneNumber, conversations);

  // console.log("대화 요약 모델 로그: ", allConversationsMap.get(phoneNumber));
  return gptContent;
}

// 대화 기록 초기화
function resetChatSummaryModelConversations(phoneNumber) {
  conversationsMap.delete(phoneNumber);
}

module.exports = {allConversationsMap, getChatSummaryModelResponse, resetChatSummaryModelConversations};
