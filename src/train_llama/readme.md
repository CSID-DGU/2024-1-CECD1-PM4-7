## LLAMA 모델 학습에 관한 폴더
### 구성
1. llama모델 다운로드 및 gguf로 양자화
2. llama모델 실행
3. llama모델 학습

### 설치
1. ```cd src/train_llama```
2. CUDA코어가 없다면 ```make all_CPU``` \
   CUDA코어가 있다면 ```make all_GPU```