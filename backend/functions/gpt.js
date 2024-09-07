// GPT API를 호출해서 응답을 가져옴
const OpenAI = require("openai");

const openai = new OpenAI({
  api_key: process.env.OPENAI_API_KEY,
});

// JSON 파일에서 프롬프트 가져오기
const fs = require("fs");
const path = require("path");
const promptPath = path.resolve(__dirname, "./prompt/prompt.json");
const promptData = JSON.parse(fs.readFileSync(promptPath, "utf-8"));
const chatPrompt = promptData.playground_chat;

// 각 클라이언트의 대화 기록
const conversations = {};

/**
 * STT로 전사된 텍스트를 GPT API에 전달하고 응답을 처리하는 함수
 * @param {string} clientId - 클라이언트를 식별 ID (각 클라이언트의 대화 기록을 독립적으로 관리하기 위해 사용)
 * @param {string} gptRequest - GPT에 전달할 요청 텍스트
 * @return {Promise<string>} GPT의 응답 텍스트
 */
async function getGPTResponse(clientId, gptRequest) {
  // 해당 클라이언트의 대화 기록이 없다면 초기화
  if (!conversations[clientId]) {
    conversations[clientId] = [
      {
        role: "system",
        content: chatPrompt,
      },
    ];
  }

  const conversationHistory = conversations[clientId];

  // 사용자의 요청을 대화 기록에 추가
  conversationHistory.push({
    role: "user",
    content: gptRequest,
  });

  // 대화 기록을 기반으로 GPT API에 응답을 요청
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: conversationHistory,
    temperature: 0.0,
    max_tokens: 256,
    top_p: 0.0,
    frequency_penalty: 0,
    presence_penalty: 0,
  });

  // gpt 응답 추출
  const gptResponse = response.choices[0].message;

  // GPT의 응답을 대화 기록에 추가
  conversationHistory.push({
    role: "assistant",
    content: gptResponse,
  });

  return gptResponse;
}

module.exports = {getGPTResponse};
