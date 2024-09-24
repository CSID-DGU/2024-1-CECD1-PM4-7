// Firebase에서 사용자의 번호를 가져와 Twilio를 통해 전화를 걸음
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const client = require("twilio")(accountSid, authToken);

const {DynamoDBClient, ScanCommand} = require('@aws-sdk/client-dynamodb');
const dynamoDbClient = new DynamoDBClient({region:'ap-northeast-2'});

/**
 * 사용자에게 전화를 거는 함수
 * @return {Promise<void>}
 */
async function callUser() {
  const params = {
    TableName: 'users', // DynamoDB 테이블 이름
  };

  try {
    // DynamoDB에서 모든 사용자 데이터를 가져옴
    const data = await dynamoDbClient.send(new ScanCommand(params));

    // for...of를 사용해 순차적으로 비동기 작업 처리
    for (const userData of data.Items) {
      const userName = userData.name.S;
      const userPhoneNumber = userData.phoneNumber.S;

      // crisisTypes는 LIst 형식이므로 각 요소의 문자열 값을 가져와 처리
      const crisisTypesArray = userData.crisisTypes.L.map(item => item.S);
      const crisisTypes = crisisTypesArray.join(', '); // 위기 유형들을 문자열로 변환

      // TwiML에서 사용자 이름을 포함한 메시지 생성
      const message = `${userName}님 본인이 맞으십니까? 맞으시다면 1번, 아니라면 2번을 눌러주세요.`;
      const gptRequest = `${userName}: ${crisisTypes}`;

      // Twilio API를 사용해 전화를 걸음
      await client.calls.create({
        url: `http://13.125.79.179/voice?message=${encodeURIComponent(message)}&gptRequest=${encodeURIComponent(gptRequest)}`,
        to: userPhoneNumber,
        from: '+12566699723',
        statusCallback: 'http://13.125.79.179/call-completed',
        statusCallbackEvent: ['completed'],
      });
    }
  } catch (error) {
    console.error('사용자에게 전화를 거는 중 오류 발생:', error);
  }
}

module.exports = {callUser};
