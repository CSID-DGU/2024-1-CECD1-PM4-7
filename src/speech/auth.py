# API 키 임포트
import os


def googleSTTAuth():
    current_dir = os.path.abspath(__file__)
    key_path = os.path.join(current_dir, '..', '..', '..', 'key', "vocal-entity-420406-b9648ba69fca.json")
    key_path = os.path.abspath(key_path)
    # 서비스 계정 키 파일의 경로를 환경 변수로 설정
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    
def googleTTSAuth():
    pass