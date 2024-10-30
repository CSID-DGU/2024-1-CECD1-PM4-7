// 대화 진행 모델
const { callOpenAI } = require("./openaiClient");
const { promptData, modelData } = require("./configLoader");

// 프롬프트, 모델명, 토큰 수 설정
const Prompt = promptData.playground_chat;
const modelName = modelData.Chat;
const maxTokens = 256;

// 각 사용자의 대화 기록을 저장
const conversationsMap = new Map();

//STT로 전사된 텍스트를 GPT API에 전달하고 응답을 처리하는 함수
async function getChatModelResponse(phoneNumber, gptInquiry) {
  // 해당 사용자의 대화 기록 가져오기
  let conversations = conversationsMap.get(phoneNumber) || [ { role: "system", content: Prompt } ];

  // 사용자의 요청을 대화 기록에 추가
  conversations.push({ role: "user", content: gptInquiry });

  // 사용자 응답에 대한 GPT 응답
  const chatResult = await callOpenAI(modelName, conversations, maxTokens);

  // 현재 대화 내용을 전체 대화 내용에 추가
  conversations.push({ role: "assistant", content: chatResult });
  conversationsMap.set(phoneNumber, conversations);

  // console.log("대화 모델 로그: ", conversations);
  return chatResult;
}

// 대화 기록 초기화
function resetChatModelConversations(phoneNumber) {
  conversationsMap.delete(phoneNumber);
}


module.exports = {conversationsMap, getChatModelResponse,  resetChatModelConversations};
