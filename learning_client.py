import requests
import os

ai_server_base_url = os.getenv('AI_SERVER_BASE_URL')

def get_AI_server(simulation_data : dict):
    resp = requests.get(url=ai_server_base_url + '/simulation-data',
                        params=simulation_data)
    if resp.status_code == 200:
        return True
    else:
        return False