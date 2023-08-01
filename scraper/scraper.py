import websocket
import json
import requests
import time
import re
import os
from requests.auth import HTTPBasicAuth
import jwt
from datetime import datetime
import authparams

images_folder = "images1"
if not os.path.exists(images_folder):
   os.makedirs(images_folder)

def shorten_string(text, max_length):
	if len(text) > max_length:
		return text[:max_length-3] + "..."
	else:        return text

def print_jwt_info(token):
	print("Token: " + shorten_string(token, 10))
	try:
		decoded_token = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
		if 'iat' in decoded_token:
			ts = decoded_token['iat']
			date = datetime.fromtimestamp(ts)
			print(f'Issued time: {date}')
		if 'exp' in decoded_token:
			ts = decoded_token['exp']
			date = datetime.fromtimestamp(ts)
			print(f'Expiration time: {date}')
		else:
			print('No expiration date.')
	except jwt.InvalidTokenError:
		print("Token not valid.")

auth_token = authparams.AUTH_TOKEN

def auth():
    print("Authenticating...")
    try:
        r = requests.post(f'https://www.reddit.com/api/v1/access_token?grant_type=password&username={authparams.USERNAME}&password={authparams.PASSWORD}',
            headers={'user-agent': 'r/place downloader'},
            auth=HTTPBasicAuth(authparams.OAUTH_CLIENT, authparams.OAUTH_SECRET))
        auth_response = json.loads(r.text)
        response_token = auth_response['access_token']
        print("Authentication successful!")
        print_jwt_info(response_token)
        return response_token
    except:
        return auth_token

currentConfig = {}
timeat = 0
big_error = False
re_auth = False

def on_message(ws, message):
    global big_error
    global re_auth
    payload = json.loads(message)
    # print(payload)
    if payload['type'] == "connection_error":
        print("Connection error!")
        if '401' in payload['payload']['message']:
            print("User is unauthorized!")
            re_auth = True
        print("Closing...")
        ws.close()
        return
    if payload['type'] != "data":
        return
    if payload['payload']['data']['subscribe']['data']['__typename'] == "ConfigurationMessageData":
        messageIndex = 2
        print(f"ConfigurationMessageData: {payload['payload']['data']['subscribe']['data']}")
        canvasConfig = payload['payload']['data']['subscribe']['data']['canvasConfigurations']
        canvasHeight = payload['payload']['data']['subscribe']['data']['canvasHeight']
        canvasWidth = payload['payload']['data']['subscribe']['data']['canvasWidth']
        activeZoneRaw = payload['payload']['data']['subscribe']['data']['activeZone']
        activeZone = {
            "startX": activeZoneRaw['topLeft']['x'],
            "startY": activeZoneRaw['topLeft']['y'],
            "endX": activeZoneRaw['bottomRight']['x'],
            "endY": activeZoneRaw['bottomRight']['y']
        }
        for configItem in canvasConfig:
            if configItem['__typename'] == "CanvasConfiguration":
                itemIndex = configItem['index']
                currentConfig[itemIndex] = {
                    "url": None,
                    "completed": False,
                    "startX": configItem['dx'],
                    "startY": configItem['dy'],
                    "endX": configItem['dx'] + canvasWidth,
                    "endY": configItem['dy'] + canvasHeight
                }
                if (currentConfig[itemIndex]["endX"] <= activeZone["startX"] or currentConfig[itemIndex]["startX"] >= activeZone["endX"]):
                    currentConfig[itemIndex]['completed'] = True
                if (currentConfig[itemIndex]["endY"] <= activeZone["startY"] or currentConfig[itemIndex]["startY"] >= activeZone["endY"]):
                    currentConfig[itemIndex]['completed'] = True
        print(f"canvasConfig: {canvasConfig}")
        for index in currentConfig.keys():
            print(f"Canvas {index}: Requesting URL...")
            if (not currentConfig[index]['completed']):
                ws.send('{"id":"' + str(messageIndex) + '","type":"start","payload":{"variables":{"input":{"channel":{"teamOwner":"GARLICBREAD","category":"CANVAS","tag":"' + str(index) +'"}}},"extensions":{},"operationName":"replace","query":"subscription replace($input:SubscribeInput!){subscribe(input:$input){id...on BasicMessage{data{__typename...on FullFrameMessageData{__typename name timestamp}...on DiffFrameMessageData{__typename name currentTimestamp previousTimestamp}}__typename}__typename}}"}}')
                messageIndex += 1
    if payload['payload']['data']['subscribe']['data']['__typename'] == "FullFrameMessageData":
        url = payload['payload']['data']['subscribe']['data']['name']
        re_result = re.search("([0-9]{13})-([0-9]{1})", url)
        extractedIndex = int(re_result.group(2))
        print(f"Canvas {extractedIndex}: Server timestamp is {re_result.group(1)}")
        currentConfig[extractedIndex]['url'] = url
        fetchImageFromUrl(url, extractedIndex, ws)

def fetchImageFromUrl(url, index, ws):
    print(f"Canvas {index}: URL obtained! Fetching...")
    global timeat
    if timeat == 0:
        timeat = int(time.time())
        print(f"Canvas {index}: Assigned time {timeat}.")
    response = requests.get(url)
    filename = f'{images_folder}/{timeat}-{index}.png'
    # print(filename)
    open(os.path.join(os.path.dirname(__file__), filename), 'wb').write(response.content)
    currentConfig[index]['completed'] = True
    print(f'Canvas {str(index)}: Fetched.')
    for configItem in currentConfig.values():
        if (not configItem['completed']):
            return
    print(f'All fetched! Closing!')
    ws.close()

def on_open(ws):
    print("Opening socket...")
    ws.send('{"type":"connection_init","payload":{"Authorization":"Bearer ' + auth_token + '"}}')
    ws.send('{"id":"1","type":"start","payload":{"variables":{"input":{"channel":{"teamOwner":"GARLICBREAD","category":"CONFIG"}}},"extensions":{},"operationName":"configuration","query":"subscription configuration($input:SubscribeInput!){subscribe(input:$input){id...on BasicMessage{data{__typename...on ConfigurationMessageData{colorPalette{colors{hex index __typename}__typename}canvasConfigurations{index dx dy __typename}activeZone{topLeft{x y __typename}bottomRight{ x y __typename} __typename}canvasWidth canvasHeight __typename}}__typename}__typename}}"}}')

if __name__ == "__main__":
    print("Launched.")
    print_jwt_info(auth_token)
    no_sleep = False

    while True:
        print(f"Top of loop: {datetime.now()}")
        timeat = 0
        try:
            print("Listening to socket...")
            currentConfig = {}
            ws = websocket.WebSocketApp("wss://gql-realtime-2.reddit.com/query", on_message=on_message, on_open=on_open)
            ws.run_forever()
            print("Socket closed.")
            if re_auth:
                print("Reauthenticating...")
                auth_token = auth()
                no_sleep = True
                time.sleep(1)
            re_auth = False

        except Exception as ex:
            auth_token = auth()
            print("ERROR")
            print(str(ex))
            # time.sleep(5)

        if not no_sleep:
            current_time = time.localtime()
            seconds_remaining = 60 - current_time.tm_sec
            print(f"Waiting {seconds_remaining} seconds...")
            time.sleep(seconds_remaining)
        no_sleep = False