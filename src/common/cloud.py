# 구글 클라우드 파일 송/수신 모듈
import os

from google.cloud import storage


# upload file
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # 조건 없이 파일 업로드
    blob.upload_from_filename(source_file_name)
    arrow_position = 50
    formatted_line = f"{source_file_name.ljust(arrow_position)} --> {destination_blob_name}"
    print(f"Upload: {formatted_line}")

def upload_folder(bucket_name, source_folder_name, destination_blob_prefix):
    files_to_upload = []

    for root, dirs, files in os.walk(source_folder_name):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            relative_path = os.path.relpath(file_path, source_folder_name)
            files_to_upload.append((file_path, file_size, relative_path))

    # 파일 크기 오름차순, 파일명 오름차순으로 정렬
    files_to_upload.sort(key=lambda x: (x[1], x[2]))

    for file_path, _, relative_path in files_to_upload:
        blob_name = os.path.join(destination_blob_prefix, relative_path)
        upload_blob(bucket_name, file_path, blob_name)



# download file
def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    blob.download_to_filename(destination_file_name)

    print(f"Download:\t{source_blob_name}")


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


# delete file
def delete_blob(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print(f"Delete:\t{blob_name}")


# delete folder
def delete_folder(bucket_name, folder_prefix):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = storage_client.list_blobs(bucket_name, prefix=folder_prefix)

    for blob in blobs:
        blob.delete()
        print(f"Delete Folder:\t{blob.name}")

# move file
def move_blob(bucket_name, source_blob_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    new_blob = bucket.copy_blob(blob, bucket, destination_blob_name) # 파일 복사
    blob.delete() # 원본 파일 삭제

    arrow_position = 50
    formatted_line = f"{source_blob_name.ljust(arrow_position)} --> {destination_blob_name}"
    print(f"Move: {formatted_line}")

# move folder
def move_folder(bucket_name, source_folder_name, destination_folder_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = storage_client.list_blobs(bucket_name, prefix=source_folder_name)

    for blob in blobs:
        # 새로운 위치로 파일 복사
        relative_path = os.path.relpath(blob.name, source_folder_name)
        new_blob_name = os.path.join(destination_folder_name, relative_path)
        move_blob(bucket_name, blob.name, new_blob_name)

        