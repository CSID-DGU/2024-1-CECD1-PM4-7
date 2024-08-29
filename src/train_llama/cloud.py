import os

from google.cloud import storage


# upload file
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

# upload folder
def upload_folder(bucket_name, source_folder_name, destination_blob_prefix):
    for root, dirs, files in os.walk(source_folder_name):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, source_folder_name)
            blob_name = os.path.join(destination_blob_prefix, relative_path)
            upload_blob(bucket_name, file_path, blob_name)


# download file
def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")


# downolad folder
def download_folder(bucket_name, source_folder_name, destination_folder_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = storage_client.list_blobs(bucket_name, prefix=source_folder_name)

    for blob in blobs:
        # GCS에서의 파일 경로를 로컬 경로로 변환
        relative_path = os.path.relpath(blob.name, source_folder_name)
        local_file_path = os.path.join(destination_folder_name, relative_path)
        
        # 폴더 구조를 유지하면서 파일 다운로드
        download_blob(bucket_name, blob.name, local_file_path)