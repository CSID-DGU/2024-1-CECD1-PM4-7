// GPT API를 호출해서 응답을 가져옴
const OpenAI = require("openai");

const openai = new OpenAI({
  api_key: process.env.OPENAI_API_KEY,
});

// JSON 파일에서 프롬프트와 모델명 가져오기
const fs = require("fs");
const path = require("path");
const promptPath = path.resolve(__dirname, "../key/prompt.json");
const promptData = JSON.parse(fs.readFileSync(promptPath, "utf-8"));
const Prompt = promptData.playground_chat;

const modelNamePath = path.resolve(__dirname, "../key/model.json");
const modelNameData = JSON.parse(fs.readFileSync(modelNamePath, "utf-8"));
const modelName = modelNameData.Chat;

// 각 클라이언트의 대화 기록
let conversations = [
  {
    role: "system",
    content: Prompt,
  },
];

/**
 * STT로 전사된 텍스트를 GPT API에 전달하고 응답을 처리하는 함수
 * @param {string} gptRequest - GPT에 전달할 요청 텍스트
 * @return {Promise<string>} GPT의 응답 텍스트
 */
async function getChatModelResponse(gptRequest) {
  // 사용자의 요청을 대화 기록에 추가
  conversations.push({
    role: "user",
    content: gptRequest,
  });

  // 대화 기록을 기반으로 GPT API에 응답을 요청
  const response = await openai.chat.completions.create({
    model: modelName,
    messages: conversations,
    temperature: 0.0,
    max_tokens: 256, //1024 요약모델
    top_p: 0.0,
    frequency_penalty: 0,
    presence_penalty: 0,
  });

  // gpt 응답 추출
  const gptResponse = response.choices[0].message;
  const gptContent = gptResponse.content;

  // GPT의 응답을 대화 기록에 추가
  conversations.push({
    role: "assistant",
    content: gptContent,
  });


  // console.log("대화 모델 로그: ", conversations);
  return gptContent;
}

// 대화 기록 초기화
function resetChatModelConversations() {
  conversations.length = 0;
  conversations.push({
    role: "system",
    content: Prompt,
  });
}


module.exports = {conversations, getChatModelResponse,  resetChatModelConversations};
