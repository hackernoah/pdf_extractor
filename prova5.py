import requests
import sys
import json

key = 'project_public_284c3eaed2a667376a2acd1959bdb2a0_bTM6dd33fa638990eb07299013a7e8f2cbb6e'
token = ''
server = ''
task_id = ''
local_filename = 'test.pdf'
server_filename = ''
auth = requests.post('https://api.ilovepdf.com/v1/auth', data={'public_key':key})
if auth.status_code == 200:
    response = json.loads(auth.text)
    token = 'Bearer ' + response['token']
    print('TOKEN: ' + token)
else:
    print(f"ERROR: http AUTHORIZATION request returned with status code {auth.status_code}")
    sys.exit()

headers = {'Authorization' : token}
# start = requests.get('https://api.ilovepdf.com/v1/start/extract', headers=headers)
# if start.status_code == 200:
#     response = json.loads(start.text)
#     task_id = response['task']
#     server = response['server']
#     print('SERVER: ' +  server)
#     print('TASK: ' + task_id)
# else:
#     print(f"ERROR: http START request returned with status code {start.status_code}")
#     print(start.content)
#     sys.exit()
 
# payload = {
#     'task' : task_id
# }
# with open('test.pdf', 'rb') as f:
#     upload = requests.post(f'https://{server}/v1/upload', headers=headers,data=payload, files = {'file': f})
#     if upload.status_code == 200:
#         response = json.loads(upload.text)
#         server_filename = response['server_filename']
#         print('FILENAME: ' + server_filename)
#     else:
#         print(f"ERROR: http UPLOAD request returned with status code {upload.status_code}")
#         print(upload.content)
#         sys.exit()

# payload = {
#     'task' : task_id,
#     'tool' : 'extract',
#     'files[0][server_filename]' : server_filename,
#     'files[0][filename]' : local_filename
# }
# process = requests.post(f'https://{server}/v1/process', headers = headers, data=payload)
# if process.status_code == 200:
#     response = json.loads(process.text)
#     print('PROCESS: ' + response['status'])
# else:
#     print(f"ERROR: http PROCESS request returned with status code {process.status_code}")
#     print(process.content)
#     sys.exit()

download = requests.get(f'https://api11.ilovepdf.com/v1/download/g27d4mrsg3ztmnzAgm5d3njAghdAjr9l36l92rpc7jwpws9fwq6nd71t4fcymb5m2dj0yAw750ryqthqs0sqqv9hwAbspyw20A3srnhq3702xqglb01xhvdtdA3hhbpx2pp2y26cAhjv4c34fn2g8fhAjm', headers = headers)
if download.status_code == 200:
    with open('test_dump', 'wb') as f:
        print(download.content)
else:
    print(f"ERROR: http DOWNLOAD request returned with status code {download.status_code}")
    print(download.content)
    sys.exit()