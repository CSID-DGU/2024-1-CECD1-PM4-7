// Firebase에서 사용자의 번호를 가져와 Twilio를 통해 전화를 걸음
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const client = require("twilio")(accountSid, authToken);

const admin = require("firebase-admin");
// 이미 초기화된 앱이 있는지 확인
if (!admin.apps.length) {
  admin.initializeApp();
}
const db = admin.firestore();

/**
 * 사용자에게 전화를 거는 함수
 * @return {Promise<void>}
 */
async function callUser() {
  // 사용자 정보 가져오기
  const usersRef = db.collection("users");
  const snapshot = await usersRef.get();

  snapshot.forEach(async (doc) => {
    const userData = doc.data();
    const userName = userData.name;
    const userPhoneNumber = userData.phoneNumber;
    const crisisTypes = userData.crisisTypes.join(", "); // 위기 유형들을 합쳐서 문자열로 변환

    // TwiML에서 사용자 이름 포함한 메시지 생성
    const message = `${userName}님 본인이 맞으십니까? 맞으시다면 1번, 아니라면 2번을 눌러주세요.`;

    // GPT에 전달할 요청 텍스트 생성
    const gptRequest = `${userName}: ${crisisTypes}`;

    await client.calls.create({
      url: `https://us-central1-welfarebot-7cbc3.cloudfunctions.net/app/voice?message=${encodeURIComponent(message)}&gptRequest=${encodeURIComponent(gptRequest)}`,
      to: userPhoneNumber,
      from: "+12566699723",
      statusCallback: "https://us-central1-welfarebot-7cbc3.cloudfunctions.net/app/call-completed",
      statusCallbackEvent: ["completed"],
    });
  });
}

module.exports = {callUser};
