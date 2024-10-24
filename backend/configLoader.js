// 프롬프트 및 모델명 가져오기
const fs = require("fs");
const path = require("path");

function loadConfig(fileName) {
  const filePath = path.resolve(__dirname, `../key/${fileName}`);
  return JSON.parse(fs.readFileSync(filePath, "utf-8"));
}

const promptData = loadConfig("prompt.json");
const modelData = loadConfig("model.json");

module.exports = { promptData, modelData };