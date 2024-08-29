# CLOVA 모델 호출
from common.auth_ import getKey, CreateTaskExecutor


completion_executor = CreateTaskExecutor(
    host='https://clovastudio.apigw.ntruss.com',
    uri='/tuning/v2/tasks',
    method='POST',
    iam_access_key=getKey('CLOVA-ACCESS'),
    secret_key=getKey('CLOVA-SECRET'),
    request_id='<request_id>'
)

request_data = {'name': 'generation_task',
                'model': 'HCX-003',
                'tuningType': 'PEFT',
                'taskType': 'GENERATION',
                'trainEpochs': '8',
                'learningRate': '1e-5f',
                # 'trainingDatasetBucket': 'bucket_name',
                # 'trainingDatasetFilePath': 'root_path/sub_path/file_name',
                # 'trainingDatasetAccessKey': 'access_key',
                # 'trainingDatasetSecretKey': 'secret_key'
                }

response_text = completion_executor.execute(request_data)
print(request_data)
print(response_text)
