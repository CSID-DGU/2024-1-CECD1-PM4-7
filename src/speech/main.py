# STT main
import STT

from common import auth_

# Auth
auth_.googleAuth()

# 변환
'''
    None 옵션은 프로그램 실행 중에 옵션을 선택할 수 있도록 함
    askFolder = True: 폴더를 선택하여 하위 모든 항목을 처리
            = False: 파일을 선택하여 처리
    makeTrainData = True: 변환 결과를 학습 데이터로도 생성
            = False: 학습 데이터를 생성하지 않음
    evaluation = True: makeTrainData를 통해 생성한 학습 데이터에서 정답을 제거
'''


STT.STT_pipeline(
    askFolder=True,
    model='google',
    makeTrainData=True,
    evaluation=True
)
