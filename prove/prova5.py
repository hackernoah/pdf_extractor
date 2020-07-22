import requests
import sys
import json

key = 'project_public_284c3eaed2a667376a2acd1959bdb2a0_bTM6dd33fa638990eb07299013a7e8f2cbb6e'
token = ''
server = ''
task_id = ''
auth = requests.post('https://api.ilovepdf.com/v1/auth', data={'public_key':key})
if auth.status_code == 200:
    response = json.loads(auth.text)
    token = 'Bearer ' + response['token']
    print(token)
else:
    print(f"ERROR: http AUTHORIZATION request returned with status code {auth.status_code}")
    sys.exit()

parameters = {'Host': 'apitest.ilovepdf.com',
'Authorization' : token,
'Cache-Control': 'no-cache'}
start = requests.get('https://api.ilovepdf.com/v1/start/extract', data=parameters)
if start.status_code == 200:
    response = json.loads(start.text)
    print(server)
    print(task_id)
    task_id = response['task']
    server = response['server']
else:
    print(f"ERROR: http START request returned with status code {start.status_code}")
    sys.exit()
 

parameters = {'Host': server,
'Authorization' : token,
'Cache-Control': 'no-cache',
'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW ------WebKitFormBoundary7MA4YWxkTrZu0gW',
'Content-Disposition': 'form-data; name="task" ' + task_id + ' ------WebKitFormBoundary7MA4YWxkTrZu0gW',
'Content-Disposition': 'form-data; name="file"; filename="test.pdf"',
'Content-Type': '------WebKitFormBoundary7MA4YWxkTrZu0gW--'}