const { GoogleSpreadsheet } = require('google-spreadsheet');
const { GoogleAuth } = require('google-auth-library');
const credentials = require(process.env.GOOGLE_APPLICATION_CREDENTIALS);
const {conversationsMap} = require("./chatModel");
const {allConversationsMap: sttConversationsMap } = require("./sttCorrectionModel");
const {allConversationsMap: summaryConversationsMap } = require("./chatSummaryModel");

const auth = new GoogleAuth({
  credentials: {
    client_email: credentials.client_email,
    private_key: credentials.private_key.replace(/\\n/g, '\n'),
  },
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
})

let authClient;
(async () => {
  authClient = await auth.getClient();
})();


// 각 모델에 대한 스프레드시트 ID
const SPREADSHEET_ID = '19dxCszQR6OVHtgLWKMUM5F5-lz2Lx-nNpIi3owRObfE';

// 최대 열 개수 설정
const MAX_COLUMNS = 30;

// 스프레드시트에 데이터를 저장하는 함수
async function saveDataToSpreadsheets(phoneNumber){
    try{
      const chatDataArray = conversationsMap.get(phoneNumber)?.map(conv => conv.content) || [];
      const sttDataArray = sttConversationsMap.get(phoneNumber)?.flatMap(conv => conv.map(c => c.content)) || [];
      const summaryDataArray = summaryConversationsMap.get(phoneNumber)?.map(conv => conv.content) || [];
  
      // 각 모델의 데이터를 해당 시트에 저장
      await saveToSpreadsheet('chat', chatDataArray);
      await saveToSpreadsheet('stt', sttDataArray);
      await saveToSpreadsheet('summary', summaryDataArray);
    } catch (error) {
      console.error(`스프레드시트 저장 오류(사용자: ${phoneNumber}):`, error);
    }
}

// 특정 스프레드시트에 데이터를 저장하는 함수
async function saveToSpreadsheet(sheetName, dataArray) {
  const doc = new GoogleSpreadsheet(SPREADSHEET_ID);
  doc.auth = authClient;  // 인증 클라이언트 설정
  await doc.loadInfo(); // 문서 정보 로드

  let sheet = doc.sheetsByTitle[sheetName]; // 시트 이름으로 접근

  const headers = generateHeaderValues();

  if (!sheet) {
    // 시트가 없으면 생성하고 헤더 행 설정
    sheet = await doc.addSheet({
      title: sheetName,
      headerValues: headers,
      gridProperties: {
        columnCount: MAX_COLUMNS,
      },
    });
  } else {
    // 시트의 열 수 확인 및 확장
    if (sheet.gridProperties.columnCount < MAX_COLUMNS) {
      await sheet.resize({ columnCount: MAX_COLUMNS });
    }

    try {
      // 헤더 행 로드 시도
      await sheet.loadHeaderRow();
    } catch (error) {
      // 헤더 행이 없으면 설정
      await sheet.setHeaderRow(headers);
    }
  }

  // 데이터 객체 생성
  const row = {};
  const length = Math.min(dataArray.length, MAX_COLUMNS);
  for (let i = 0; i < length; i++) {
    row[`content${i + 1}`] = dataArray[i];
  }

  // 데이터 추가
  await sheet.addRow(row);
  console.log(`시트 ${sheetName}에 데이터 추가 완료`);
}

function generateHeaderValues() {
  const headers = [];
  for (let i = 0; i < MAX_COLUMNS; i++) {
    headers.push(`content${i + 1}`);
  }
  return headers;
}

module.exports = { saveDataToSpreadsheets };
