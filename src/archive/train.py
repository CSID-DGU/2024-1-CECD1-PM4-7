# 학습 진행
import time
from common.auth_ import getKey
from evaluate import evaluation
import openai
from pathlib import Path
from common.info import open_dialog, updateModelName


# 작업 상태 확인
def check_fine_tune_status(fine_tune_id):
    response = openai.FineTune.retrieve(id=fine_tune_id)
    status = response['status']
    return status

# 학습
def train(model_name: str, filepath: Path, evaluate: bool) -> bool:
    try:
        openai.api_key = getKey('STT')

        # 학습 데이터 준비
        response = openai.File.create(
            file=open(str(filepath), 'rb'),
            purpose='fine-tune'
        )
        file_id = response['id']
        print(f"File ID: {file_id} uploaded.")

        # 학습 시작
        response = openai.FineTune.create(
            training_file=file_id,
            model=model_name
        )
        fine_tune_id = response['id']
        print(f"Fine-tune ID: {fine_tune_id} start.")

        # 진행 상황 모니터링
        status = check_fine_tune_status(fine_tune_id)
        while status not in ["succeeded", "failed"]:
            print(f"Current status: {status}")
            time.sleep(30)  # 30초 간격으로 상태 확인
            status = check_fine_tune_status(fine_tune_id)

        print(f"Final status: {status}")

        if status == "succeeded":
            print("학습 성공")
            # 신규 모델 이름
            fine_tuned_model = openai.FineTune.retrieve(id=fine_tune_id)['fine_tuned_model']
            print(f"신규 모델: {fine_tuned_model}")
            updateModelName('STT', fine_tuned_model)
            # 검증
            if evaluate:
                print("검증 시작")
                evaluation(fine_tuned_model)
            else:
                print("검증 없이 종료합니다..")
            return True
        else:
            print("학습 실패")
    except Exception as e:
        print(f"오류 발생: {e}")
        return False
