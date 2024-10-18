// Firebase에서 사용자의 번호를 가져와 Twilio를 통해 전화를 걸음
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const client = require("twilio")(accountSid, authToken);

const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, GetCommand } = require('@aws-sdk/lib-dynamodb');

const dynamoDbClient = new DynamoDBClient({ region: 'ap-northeast-2' });
const dynamoDbDocClient = DynamoDBDocumentClient.from(dynamoDbClient);

/**
 * 사용자에게 전화를 거는 함수
 * @return {Promise<void>}
 */
async function callUser(phoneNumber) {
  // DynamoDB에서 해당 사용자의 데이터 가져오기
  const params = {
    TableName: 'users',
    Key: { 'phoneNumber': phoneNumber },
  };

  const data = await dynamoDbDocClient.send(new GetCommand(params));
  
  if (!data.Item) {
    throw new Error('해당 전화번호의 사용자를 찾을 수 없습니다.');
  }


  const userData = data.Item;
  const userName = userData.name;
  const crisisTypesArray = userData.crisisTypes || [];
  const crisisTypes = crisisTypesArray.join(', '); // 위기 유형들을 문자열로 변환
    
  // TwiML에서 사용자 이름을 포함한 메시지 생성
  const message = `${userName}님 본인이 맞으십니까? 맞으시다면 1번, 아니라면 2번을 눌러주세요.`;
  const gptRequest = `${userName}: ${crisisTypes}`;

  // Twilio API를 사용해 전화를 걸음
  await client.calls.create({
    url: `https://welfarebot.kr/voice?message=${encodeURIComponent(message)}&gptRequest=${encodeURIComponent(gptRequest)}`,
    to: phoneNumber,
    from: '+12566699723',
    // statusCallback: 'http://13.125.79.179/call-completed',
    // statusCallbackEvent: ['completed'],
  });
}

module.exports = {callUser};
