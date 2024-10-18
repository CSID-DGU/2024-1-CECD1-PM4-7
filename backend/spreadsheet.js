const { GoogleSpreadsheet } = require('google-spreadsheet');

const client = new TextToSpeechClient({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
});

const {conversationsMap} = require("./chatModel");
const {allConversationsMap: sttConversationsMap } = require("./sttCorrectionModel");
const {allConversationsMap: summaryConversationsMap } = require("./chatSummaryModel");

// 각 모델에 대한 스프레드시트 ID
const SPREADSHEET_ID_CHAT = 'your-chat-model-sheet-id';
const SPREADSHEET_ID_STT = 'your-stt-correction-sheet-id';
const SPREADSHEET_ID_SUMMARY = 'your-summary-model-sheet-id';

// 스프레드시트에 데이터를 저장하는 함수
async function saveDataToSpreadsheets(){
    try{
      const chatData = conversationsMap.get(phoneNumber)?.map(conv => conv.content).join('\n') || '';
      const sttData = sttConversationsMap.get(phoneNumber)?.flatMap(conv => conv.map(c => c.content)).join('\n') || '';
      const summaryData = summaryConversationsMap.get(phoneNumber)?.map(conv => conv.content).join('\n') || '';
  
      // 각 모델의 데이터를 스프레드시트에 저장
      await saveToSpreadsheet(SPREADSHEET_ID_CHAT, chatData);
      await saveToSpreadsheet(SPREADSHEET_ID_STT, sttData);
      await saveToSpreadsheet(SPREADSHEET_ID_SUMMARY, summaryData);
      console.log(`스프레드 시트에 데이터 저장 완료(사용자: ${phoneNumber})`);
    } catch (error) {
      console.error('스프레드시트 저장 오류(사용자: ${phoneNumber}):', error);
      res.status(500).send('스프레드시트 저장 오류(사용자: ${phoneNumber})');
    }
}

// 특정 스프레드시트에 데이터를 저장하는 함수
async function saveToSpreadsheet(sheetId, data) {
  const doc = new GoogleSpreadsheet(sheetId);
  await doc.useServiceAccountAuth(credentials);
  await doc.loadInfo(); // 문서 정보 로드

  const sheet = doc.sheetsByIndex[0]; // 첫 번째 시트를 사용
  await sheet.addRow({ content: data });
}

module.exports = { saveDataToSpreadsheets };
