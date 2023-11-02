import urllib.request
from slack_sdk import WebClient
from flask import Flask
import datetime
import json
from config import app_token, bot_token, channel_id, url


def get_from_api(where=""):
    url = "http://165.246.44.85:5000/get?where={where}"

    response = urllib.request.urlopen(url)  # URL을 엽니다. # 응답 데이터를 읽습니다.
    data = response.read().decode("utf-8")
    data = data.replace("'", '"')
    print(data)
    data = json.loads(data)
    response.close()
    return data


def this_weekday():
    return datetime.datetime.now().strftime("%A")

def today():
    return datetime.datetime.now().strftime("%Y년 %m월 %d일")

def parse_json_to_message(json_data):
    today_of_week = this_weekday()
    today_hak = json_data['hak'][today_of_week]
    today_gyo = json_data['gyo'][today_of_week]['breakfast'].replace("\t\t", "").split('\n')
    today_gyo = [item for item in today_gyo if item != ""]
    print(today_gyo)
    today_gi = json_data['gi'][today_of_week]

    hak_message = f'*학생식당*\n\n✨ 조식 ✨\n{today_hak["breakfast"]}\n\n☀ 중식 ☀\n{today_hak["lunch"]}\n\n🌙 석식 🌙\n{today_hak["dinner"]}\n\n\n'
    gyo_message = f'*교직원식당*\n\n✨ 조식 ✨\n{today_gyo[0]}\n{today_gyo[1]}\n\n☀ 중식 ☀\n{today_gyo[2]}\n(백반)\n{today_gyo[3]}\n\n(특식)\n{today_gyo[5]}\n\n\n🌙 석식 🌙\n{today_gyo[6]}\n{today_gyo[7]}\n\n\n'
    gi_message = f'*생활관식당*\n\n✨ 조식 ✨\n{today_gi["breakfast"]}\n\n☀ 중식 ☀\n{today_gi["lunch"]}\n\n🌙 석식 🌙\n{today_gi["dinner"]}\n\n🌭 간편식 🌭\n{today_gi["easy_meal"]}\n\n\n'

    return f'✉ 학식왕 김인하 - {today()} 식단 ✉\n\n\n{hak_message}\n{gyo_message}\n{gi_message}\n\n식사 맛있게 하세요!'



app = Flask("__name__")
app.config['JSON_AS_ASCII'] = False



def send_message_to_channel(message):
    slack_client = WebClient(token=bot_token)
    slack_client.chat_postMessage(
        channel=channel_id,
        text=message
    )



@app.get('/')
def index():
    week_json = get_from_api()
    today_message = parse_json_to_message(week_json)
    send_message_to_channel(today_message)
    print(today_message)
    return today_message


if __name__ == "__main__":
    app.run("0.0.0.0", port=5001, debug=False)





# import json
# import urllib.request
# import Flask
# import WebClient
# import datetime
# import json


# channel_id = 'C05FV3HCTHT'
# app_token= 'xapp-1-A0638MTUASH-6126305421777-a39d6b35596daa9380e9b0d65026667bbc75c57c084991aed487c9e0984e7c56'
# bot_token = 'xoxb-5565757234368-6126325981553-qURGNulzVPQayReIHrH3qs2I'

# url={
#     'student':'https://www.inha.ac.kr/kr/1072/subview.do',
#     'professor': 'https://www.inha.ac.kr/kr/1073/subview.do',
#     'dormitory':'https://dorm.inha.ac.kr/dorm/10136/subview.do'
# }

# def lambda_handler(event, context):
#     week_json = get_from_api()
#     today_message = parse_json_to_message(week_json)
#     send_message_to_channel(today_message)
#     # TODO implement
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Hello from Lambda!')
#     }



# def get_from_api(where=""):
#     url = "http://165.246.44.85:5000/get?where={where}"

#     response = urllib.request.urlopen(url)  # URL을 엽니다. # 응답 데이터를 읽습니다.
#     data = response.read().decode("utf-8")
#     data = data.replace("'", '"')
#     print(data)
#     data = json.loads(data)
#     response.close()
#     return data


# def this_weekday():
#     return datetime.now().strftime("%A")

# def today():
#     return datetime.now().strftime("%Y년 %m월 %d일")

# def parse_json_to_message(json_data):
#     today_of_week = this_weekday()
#     today_hak = json_data['hak'][today_of_week]
#     today_gyo = json_data['gyo'][today_of_week]['breakfast'].replace("\t\t", "").split('\n')
#     today_gyo = [item for item in today_gyo if item != ""]
#     print(today_gyo)
#     today_gi = json_data['gi'][today_of_week]

#     hak_message = f'*학생식당*\n\n✨ 조식 ✨\n{today_hak["breakfast"]}\n\n☀ 중식 ☀\n{today_hak["lunch"]}\n\n🌙 석식 🌙\n{today_hak["dinner"]}\n\n\n'
#     gyo_message = f'*교직원식당*\n\n✨ 조식 ✨\n{today_gyo[0]}\n{today_gyo[1]}\n\n☀ 중식 ☀\n{today_gyo[2]}\n(백반)\n{today_gyo[3]}\n\n(특식)\n{today_gyo[5]}\n\n\n🌙 석식 🌙\n{today_gyo[6]}\n{today_gyo[7]}\n\n\n'
#     gi_message = f'*생활관식당*\n\n✨ 조식 ✨\n{today_gi["breakfast"]}\n\n☀ 중식 ☀\n{today_gi["lunch"]}\n\n🌙 석식 🌙\n{today_gi["dinner"]}\n\n🌭 간편식 🌭\n{today_gi["easy_meal"]}\n\n\n'

#     return f'✉ 학식왕 김인하 - {today()} 식단 ✉\n\n\n{hak_message}\n{gyo_message}\n{gi_message}\n\n식사 맛있게 하세요!'



# def send_message_to_channel(message):
#     slack_client = WebClient(token=bot_token)
#     slack_client.chat_postMessage(
#         channel=channel_id,
#         text=message
#     )

