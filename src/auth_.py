# API 키 임포트
import os
import json

current_dir = os.path.abspath(__file__)
key_folder = os.path.join(current_dir, '..', '..', 'key')
key_folder = os.path.abspath(key_folder)

# openAI Auth
def openAIAuth():
    key_path = os.path.join(key_folder, 'STT.json')
    with open(key_path, 'r', encoding='utf-8') as f:
        key_data = json.load(f)

    return key_data["STT"]

# prompt
def getPrompt(name: str):
    promptPath = os.path.abspath(os.path.join(current_dir, '..', '..', 'public', 'prompt.json'))
    with open(promptPath, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    prompt = prompt_data[name]
    return prompt

# google Auth
def googleSTTAuth():
    key_path = os.path.join(key_folder, "vocal-entity-420406-b9648ba69fca.json")
    # 서비스 계정 키 파일의 경로를 환경 변수로 설정
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    
def googleTTSAuth():
    pass