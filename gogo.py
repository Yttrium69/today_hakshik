import json
import urllib.request
from slack_sdk import WebClient
import datetime


# 학식왕 김인하
app_token = 'xapp-1-A064ZPC4YGY-6159442494193-53328f2ee39e3ddf2d8b5bd567020a6f93ddbb88577e88aafea2f9138a3365da'
bot_token = 'xoxb-6159436936209-6143884905333-SMGGGGazwfwedCnRWsZ7XBC5'
# channel_id = 'C06493MQ9T4' #public
channel_id = 'C0647S9P8S1'  # admin


def send_message_to_channel(message):
    slack_client = WebClient(token=bot_token)
    slack_client.chat_postMessage(
        channel=channel_id,
        text=message
    )


send_message_to_channel("관리자 테스트")
