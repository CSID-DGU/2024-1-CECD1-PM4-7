// DynamoDB와 관련된 작업을 처리
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const client = require("twilio")(accountSid, authToken);

const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, ScanCommand, GetCommand, UpdateCommand } = require('@aws-sdk/lib-dynamodb');

// DocumentClient 생성
const dynamoDbClient = new DynamoDBClient({ region: 'ap-northeast-2' });
const dynamoDbDocClient = DynamoDBDocumentClient.from(dynamoDbClient);

// 전화 번호 목록 가져오기
async function getPhoneNumbers() {
  const params = {
    TableName: "users",
    ProjectionExpression: "phoneNumber",
  };

  const data = await dynamoDbDocClient.send(new ScanCommand(params));
  return data.Items.map(item => item.phoneNumber);
}

// 위기 유형 가져오기
async function getCrisisTypes(phoneNumber) {
  const params = {
    TableName: 'users',
    Key: { 'phoneNumber': phoneNumber },
  };

  const data = await dynamoDbDocClient.send(new GetCommand(params));
  return data.Item?.crisisTypes || [];
}

// 위기 유형 업데이트
async function updateCrisisTypes(phoneNumber, crisisTypes) {
  const params = {
    TableName: 'users',
    Key: { 'phoneNumber': phoneNumber },
    UpdateExpression: 'SET crisisTypes = :crisisTypes',
    ExpressionAttributeValues: {
      ':crisisTypes': crisisTypes,
    },
  };

  await dynamoDbDocClient.send(new UpdateCommand(params));
}

// 사용자에게 전화 걸기
async function callUser(phoneNumber) {
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
  // const message = `${userName}님 본인이 맞으십니까? 맞으시다면 1번, 아니라면 2번을 눌러주세요.`;
  const gptRequest = `${userName}: ${crisisTypes}`;

  // Twilio API를 사용해 전화를 걸음
  await client.calls.create({
    url: `https://welfarebot.kr/voice?phoneNumber=${encodeURIComponent(phoneNumber)}&gptRequest=${encodeURIComponent(gptRequest)}`,
    to: phoneNumber,
    from: '+12566699723'
  });
}

module.exports = {getPhoneNumbers, getCrisisTypes, updateCrisisTypes, callUser};
