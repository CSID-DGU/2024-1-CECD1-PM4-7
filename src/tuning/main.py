# STT 학습 진행
from train import train
from common.info import getModelName, open_dialog

# 모델명
model_name = getModelName('STT')

# 학습 진행
train_file_path = open_dialog(False, "학습 데이터 파일을 선택해주세요.", 0.3)
'''
    model_name:         모델명
    train_file_path:    학습 데이터 파일
    evaluate:           검증 여부
'''
train(model_name=model_name,
      filepath=train_file_path,
      evaluate=False)

