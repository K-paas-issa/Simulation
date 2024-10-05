from fastapi import FastAPI
import os
import boto3
import datetime
import requests
from pytz import timezone, utc

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
access_key = os.getenv('NCP_ACCESSKEY')
secret_key = os.getenv('NCP_SECRETKEY')

app = FastAPI()

@app.get("/simulation-data")
def learning(simulation_data):
    download_path = download_csv(simulation_data) # ai_input.csv로 다운받은 상태.
    print(download_path)

    # 다운받은 csv파일의 경로 매개변수, 실제로 학습하는 함수
    # learning_res는 ai.output.csv 문자열
    learning_res = start_learning(download_path) 

    # upload_path는 'ai/ai_output_현재시간.csv' 문자열
    upload_path = upload_csv(learning_res)

    return upload_path


def upload_csv(local_file_path): # local_file_path는 학습 결과로 나온 csv가 로컬에 저장된 상태일 때 그 경로.
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    bucket_name = 'contest73-bucket'

    # create folder
    folder_name = 'ai/'

    s3.put_object(Bucket=bucket_name, Key=folder_name)

    # upload file
    now = datetime.utcnow()
    KST = timezone('Asia/Seoul')
    kst_time = utc.localize(now).astimezone(KST)
    object_name = f'{folder_name}/ai_output_{kst_time}.csv'
    try:
        s3.upload_file(local_file_path, bucket_name, object_name)
        return object_name
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # 예외 메시지 출력
        return 'exception throws'




def start_learning(ai_input_data):
# 매개변수는 다운받은 ai_input.csv파일
# 실제 학습이 진행되는 함수
# TODO : 실제 학습 부분 구현
# 여기서 학습 결과로 나온 csv파일 ai_output.csv로 저장할 것
    return




def download_csv(simulation_data):
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    bucket_name = 'contest73-bucket'

    local_file_path = 'ai_input.csv'
    try:
        s3.download_file(bucket_name, simulation_data, local_file_path)
        return local_file_path
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # 예외 메시지 출력
        return 'exception throws'