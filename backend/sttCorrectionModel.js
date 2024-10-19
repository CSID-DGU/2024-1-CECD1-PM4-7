// GPT API를 호출해서 응답을 가져옴
const OpenAI = require("openai");

const openai = new OpenAI({
  api_key: process.env.OPENAI_API_KEY,
});

// JSON 파일에서 프롬프트 가져오기
const fs = require("fs");
const path = require("path");
const promptPath = path.resolve(__dirname, "../key/prompt.json");
const promptData = JSON.parse(fs.readFileSync(promptPath, "utf-8"));
const Prompt = promptData.stt_correction_241015;

const modelNamePath = path.resolve(__dirname, "../key/model.json");
const modelNameData = JSON.parse(fs.readFileSync(modelNamePath, "utf-8"));
const modelName = modelNameData.stt_correction;

// 각 사용자의 대화 기록을 저장
const allConversationsMap = new Map();


// STT로 전사된 텍스트를 GPT API에 전달하고 응답을 처리하는 함수
async function getSttCorrectionModelResponse(phoneNumber, gptRequest, chatModelResponse) {
  // gpt 응답을 바탕으로 프롬프트 재구성
  const modifiedPrompt = Prompt.replace("{}", `"${chatModelResponse}"`);

  // GPT API에 보낼 메세지 구성
  const conversations = [
    {
      role: "system",
      content: modifiedPrompt,
    },
    {
      role: "user",
      content: gptRequest,
    },
  ];

  // GPT API에 응답 요청
  const response = await openai.chat.completions.create({
    model: modelName,
    messages: conversations,
    temperature: 0.0,
    max_tokens: 256,
    top_p: 0.0,
    frequency_penalty: 0,
    presence_penalty: 0,
  });

  // gpt 응답 추출
  const gptResponse = response.choices[0].message;
  const gptContent = gptResponse.content;

  conversations.push({
    role: "assistant",
    content: gptContent,
  });

  // 현재 대화 내용을 해당 사용자의 전체 대화 내용에 추가
  let userConversations = allConversationsMap.get(phoneNumber) || [];
  userConversations.push(conversations);
  allConversationsMap.set(phoneNumber, userConversations);

  // console.log("stt 교정 모델 로그: ", allConversationsMap.get(phoneNumber));
  return gptContent;
}

// 대화 기록 초기화
function resetSttCorrectionModelConversations(phoneNumber) {
  allConversationsMap.delete(phoneNumber);
}

module.exports = {allConversationsMap,getSttCorrectionModelResponse, resetSttCorrectionModelConversations};
