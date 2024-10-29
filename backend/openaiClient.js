// OpenAI 초기화 및 GPT API 호출
const OpenAI = require("openai");

const openai = new OpenAI({
  api_key: process.env.OPENAI_API_KEY,
});

// GPT API 호출
async function callOpenAI(modelName, messages, maxTokens = 256) {
  const response = await openai.chat.completions.create({
    model: modelName,
    messages: messages,
    temperature: 0.0,
    max_tokens: maxTokens,
    top_p: 0.0,
    frequency_penalty: 0,
    presence_penalty: 0,
  });

  return response.choices[0].message.content;
}

module.exports = { callOpenAI };