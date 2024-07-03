# 동국대학교 컴퓨터공학과 2024 종합설계 팀 PM4

---
### 설치
#### ffmpeg
1. ```https://github.com/BtbN/FFmpeg-Builds/releases``` 접속,<br/> ```ffmpeg-master-latest-win64-gpl-shared.zip``` 다운로드
2. 압축풀기 후 ```C:/ffmpeg``` 배치

#### 필요한 모듈 설치(setup.py)
프로젝트 ```root directory```에서 진행
```cmd
pip install -e .
```
### 키 배치
```/key``` 내부에 키 파일 배치(google, OpenAI)

---
### 프롬프트 수정
```/key``` 폴더 하위 ```prompt.json```

### playground 실행
```/src/playground/main.py```

### STT 실행
```/src/speech/main.py```
