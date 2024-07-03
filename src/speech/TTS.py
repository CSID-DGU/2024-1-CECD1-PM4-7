# Todo: GTTS -> select voiceline
from gtts import gTTS

# 변환할 텍스트
text = "안녕하세요. 이것은 테스트용 음성 파일입니다."

# gTTS 객체 생성
tts = gTTS(text=text, lang='ko')

# 음성 파일 저장
tts.save("test_audio.wav")

print("음성 파일이 생성되었습니다: test_audio.wav")
