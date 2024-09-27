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
ai_server_base_url = os.getenv('AI_SERVER_BASE_URL')

app = FastAPI()

@app.get("/climate-data")
def simulation(object_name):
    download_res = download_csv(object_name) # simulation_input.csv로 다운받은 상태.
    print(download_res)

    # 실질적으로 이 함수 내부에서 시뮬레이션 하는 코드 작성할 것. csv도 알아서 접근할 것.
    # 이 함수에서 시뮬레이션 돌려서 나온 값을 csv로 저장. csv이름은 simulation_output.csv로 할 것.
    simulation_implementation('simulation_input.csv') 

    # simulation_output_ + 현재 시간 + .csv 형식으로 파일 업로드
    # upload_csv 응답값 : ncp object에 올라간 시뮬레이션 csv파일 경로
    upload_simulation_data_res = upload_csv('simulation_output.csv')
    print(upload_simulation_data_res)

    final_res = get_AI_server(upload_simulation_data_res) # AI서버로 http 통신 날리기
    
    return {"filePath" : final_res}

def get_AI_server(simulation_data):
    resp = requests.get(url=ai_server_base_url + '/simulation-data',
                        params=simulation_data)
    if resp.status_code == 200:
        return resp.text # ai의 output이 ncp object에 저장되어 있는 경로(string) 반환
    else:
        return 'http request exception'

def simulation_implementation(simulation_input_data):

# 여기다가 시뮬레이션 코드 작성할 것.
    return

def download_csv(object_name):
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    bucket_name = 'contest73-bucket'

    local_file_path = 'simulation_input.csv'
    try:
        s3.download_file(bucket_name, object_name, local_file_path)
        return 'success'
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # 예외 메시지 출력
        return 'exception throws'
    

def upload_csv(local_file_path): # local_file_path는 시뮬레이션 결과로 나온 csv가 로컬에 저장된 상태일 때 그 경로.
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    bucket_name = 'contest73-bucket'

    # create folder
    folder_name = 'simulation/'

    s3.put_object(Bucket=bucket_name, Key=folder_name)

    # upload file
    now = datetime.utcnow()
    KST = timezone('Asia/Seoul')
    kst_time = utc.localize(now).astimezone(KST)
    object_name = f'{folder_name}/simulation_output_{kst_time}.csv'
    try:
        s3.upload_file(local_file_path, bucket_name, object_name)
        return object_name
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # 예외 메시지 출력
        return 'exception throws'