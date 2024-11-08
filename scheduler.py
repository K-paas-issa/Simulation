from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from db_models import DisasterNotification
import disaster_repository as repo
import requests
import os
import simulation_service
import asyncio

disaster_data_url = 'https://www.safetydata.go.kr/V2/api/DSSP-IF-00247'
disaster_data_api_key = os.getenv('DISASTER_DATA_API_KEY')

def check_keyword():
    today = datetime.now().strftime('%Y%m%d')
    payloads = {
        "serviceKey" : disaster_data_api_key, # disaster_data_api_key로 대체
        "returnType" : 'json',
        "pageNo": '1',
        'numOfRows' : '50',
        'crtDt' : today
    }
    response = requests.get(disaster_data_url, params=payloads)
    # API 호출
    print(response.status_code)
    if response.status_code != 200 or response.json()['body'] == None:
        print('reqeust fail')
        return

    data = response.json()['body']

    if data == None:
        print('body not exist')
        return

    learning_flag = False
    
    for element in data:
        message = element['MSG_CN']
        if '오물 풍선' in message or '오물풍선' in message or '쓰레기풍선' in message or '쓰레기 풍선' in message or ('북한' in message and '쓰레기' in message) or ('북한' in message and '오물' in message):
            if repo.existBySn(element['SN']):
                continue
            disaster_notification = DisasterNotification(
                element['SN'],
                message,
                element['RCPTN_RGN_NM'],
                datetime.strptime((element['CRT_DT']), "%Y/%m/%d %H:%M:%S")
            )
            repo.save(disaster_notification)
            # 객체 생성 및 저장.
            learning_flag = True # 학습해야함.
        
    return learning_flag

async def check_keyword_and_run_simulation():
    print('scheduling start')
    is_exist_data = check_keyword()
    print('is_exist_data : ', is_exist_data)
    if is_exist_data:
        #시뮬레이션 시작
        print('detect disaster keyword. start simulation')
        await simulation_service.simulation_start()
    else:
        print('does not detect disaster keyword')

def run_async():
    asyncio.run(check_keyword_and_run_simulation())

# 스케줄러 설정
scheduler = BackgroundScheduler()
scheduler.add_job(run_async, 'interval', minutes=5)
scheduler.start()
