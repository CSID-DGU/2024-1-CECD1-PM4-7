// 파이어스토어에 데이터 저장
const admin = require("firebase-admin");
admin.initializeApp();
const db = admin.firestore();

/**
 * 사용자의 정보를 Firestore에 추가
 * @param {string} name
 * @param {string} phoneNumber
 * @param {Array} crisisTypes
 * @return {Promise<void>}
 */
async function addUser(name, phoneNumber, crisisTypes) {
  try {
    await db.collection("users").add({
      name: name,
      phoneNumber: phoneNumber,
      crisisTypes: crisisTypes,
    });
    console.log("사용자 정보가 성공적으로 저장됨");
  } catch (error) {
    console.error("사용자 정보를 저장하는 과정에서 오류 발생: ", error);
  }
}

module.exports = {addUser};
