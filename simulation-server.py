from fastapi import FastAPI, BackgroundTasks
import os
import boto3
import requests
import tt
from datetime import datetime, timezone as dt_timezone
from pytz import timezone as pytz_timezone, utc
from fastapi import status
from fastapi import Response

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
access_key = os.getenv('NCP_ACCESSKEY')
secret_key = os.getenv('NCP_SECRETKEY')
ai_server_base_url = os.getenv('AI_SERVER_BASE_URL')
spring_server_base_url = os.getenv('SPRING_SERVER_BASE_URL')
climate_data_api_key = os.getenv('CLIMATE_DATA_API_KEY')

app = FastAPI()

@app.get("/climate-data-get")
def get_climate_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(simulation_test)
    return Response(status_code=status.HTTP_202_ACCEPTED)

def simulation_test():
    try:
        headers = {
            'BK-API-KEY': climate_data_api_key,  # 예시: Bearer 토큰
            'Content-Type': 'application/json'
        }
        print('climate data get request start')
        resp = requests.get(url=ai_server_base_url + '/api/climate/data-path',
                            headers=headers)  # headers 추가
        print('climate data get request end')
        if resp.status_code == 200:
            print('spring request success')
            res_json = resp.json()
            return simulation_body(res_json['dataPath'])
        else:
            print('spring request fail')
            return False
    except Exception as e:
        print(f"Error in simulation_test: {str(e)}")

@app.get("/climate-data")
def simulation(object_name: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(simulation_body, object_name)
    return Response(status_code=status.HTTP_202_ACCEPTED)

def simulation_body(object_name: str) :
    print('start simulation body')
    file_name = download_csv(object_name) # simulation_input.csv로 다운받은 상태.
    print(file_name)

    # 실질적으로 이 함수 내부에서 시뮬레이션 하는 코드 작성할 것. csv도 알아서 접근할 것.
    # 이 함수에서 시뮬레이션 돌려서 나온 값을 csv로 저장. csv이름은 simulation_output.csv로 할 것.
    simulation_output = simulation_implementation(file_name)

    # simulation_output_ + 현재 시간 + .csv 형식으로 파일 업로드
    # upload_csv 응답값 : ncp object에 올라간 시뮬레이션 csv파일 경로
    upload_simulation_data_res = upload_csv(simulation_output) 
    print(upload_simulation_data_res)

    final_res = get_AI_server({'path' : upload_simulation_data_res}) # AI서버로 http 통신 날리기
    if final_res==True:
        print('reqeust success')
    else:
        print('request fail')



def get_AI_server(simulation_data : dict):
    resp = requests.get(url=ai_server_base_url + '/simulation-data',
                        params=simulation_data)
    if resp.status_code == 200:
        return True
    else:
        return False

def simulation_implementation(simulation_input_data):
    simulation_output = tt.main(simulation_input_data)
# 여기다가 시뮬레이션 코드 작성할 것.
    return simulation_output

def download_csv(object_name):
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    bucket_name = 'contest73-bucket'

    local_file_path = 'simulation_input.csv'
    try:
        s3.download_file(bucket_name, object_name, local_file_path)
        return local_file_path
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # 예외 메시지 출력
        return 'exception throws'
    

def upload_csv(local_file_path): # local_file_path는 시뮬레이션 결과로 나온 csv가 로컬에 저장된 상태일 때 그 경로.
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    bucket_name = 'contest73-bucket'

    # create folder
    folder_name = 'simulation'

    s3.put_object(Bucket=bucket_name, Key=folder_name)

    # upload file
    now = datetime.now(dt_timezone.utc)
    KST = pytz_timezone('Asia/Seoul')
    kst_time = now.astimezone(KST)
    kst_time_str = kst_time.strftime('%Y%m%d_%H%M%S')
    object_name = f'{folder_name}/simulation_output_{kst_time_str}.npy'
    try:
        s3.upload_file(local_file_path, bucket_name, object_name)
        return object_name
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # 예외 메시지 출력
        return 'exception throws'