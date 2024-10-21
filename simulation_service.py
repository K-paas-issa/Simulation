import os
import requests
import s3utils
import learning_client
import tt
import time

spring_server_base_url = os.getenv('SPRING_SERVER_BASE_URL')
climate_data_api_key = os.getenv('CLIMATE_DATA_API_KEY')


def get_simulation_data_path():
    try:
        headers = {
            'BK-API-KEY': climate_data_api_key,  # 예시: Bearer 토큰
            'Content-Type': 'application/json'
        }
        print('climate data get url is   ', spring_server_base_url, '/api/climate/data-path')
        print('climate data get request start')
        resp = requests.get(url=spring_server_base_url + '/api/climate/data-path',
                            headers=headers)  # headers 추가
        print('climate data get request end')
        if resp.status_code == 200:
            print('spring request success')
            res_json = resp.json()
            print('res : ', res_json)
            print('data path : ', res_json['dataPath'])
            return res_json['dataPath']
        else:
            print('spring request fail')
            print(resp.status_code)
            print(resp.text)
            return False
    except Exception as e:
        print(f"Error in simulation_test: {str(e)}")

def simulation_start():
    print('simulation_start')
    data_path = get_simulation_data_path()
    simulation_body(data_path)
    return

async def simulation_body(object_name: str) :
    print('start simulation body')
    file_name = s3utils.download_csv(object_name) # simulation_input.csv로 다운받은 상태.
    print(file_name)

    # 실질적으로 이 함수 내부에서 시뮬레이션 하는 코드 작성할 것. csv도 알아서 접근할 것.
    # 이 함수에서 시뮬레이션 돌려서 나온 값을 csv로 저장. csv이름은 simulation_output.csv로 할 것.
    for i in range(5): #임시로 5번 TODO : 10번으로 바꾸기
        simulation_output = tt.main(file_name)

    # simulation_output_ + 현재 시간 + .csv 형식으로 파일 업로드
    # upload_csv 응답값 : ncp object에 올라간 시뮬레이션 csv파일 경로
        upload_simulation_data_res = s3utils.upload_csv(simulation_output) 
        print(upload_simulation_data_res)

        final_res = learning_client.get_AI_server({'path' : upload_simulation_data_res}) # AI서버로 http 통신 날리기
        if final_res==True:
            print('reqeust success')
        else:
            print('request fail')
        await time.sleep(180)
        
        
