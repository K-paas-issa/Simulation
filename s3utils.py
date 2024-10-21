import boto3
import os
from pytz import timezone as pytz_timezone, utc
from datetime import datetime, timezone as dt_timezone

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
access_key = os.getenv('NCP_ACCESSKEY')
secret_key = os.getenv('NCP_SECRETKEY')

def download_csv(object_name):
    print('download_csv start, data-path : ', object_name)
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