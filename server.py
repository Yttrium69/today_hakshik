from flask import Flask, render_template, jsonify, redirect, url_for
import requests
import time
from config import app_token, bot_token, channel_id, url
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from bs4 import BeautifulSoup
import datetime
import json

app_slack = App(token=app_token)
slack_client = WebClient(token=bot_token)


def parse_meal(when, html_doc):
    def makeup_menu(target_json):
        res_arr = []
        for json in target_json:
            res_arr.append(f'[{json.get("menu")}({json["price"]})]\n{json["food"]}')
        return '\n\n'.join(res_arr)
    
    def parse_meal_idx(when):
        day_of_week_idx =  -1
        when_idx = -1
        day_of_week_idx = datetime.date.today().weekday()
        
        if(when == 'breakfast'):
            when_idx = 0
        elif(when=='lunch'):
            when_idx = 1
        elif(when=='self'):
            when_idx = 2
        elif(when=='dinner'):
            when_idx = 3
        
        
        return 4*day_of_week_idx + when_idx
    
    
    def parse_menu_json(when, html_doc):
        meal_idx = parse_meal_idx(when)
        soup = BeautifulSoup(html_doc, "html.parser", from_encoding='utf-8')
        menu_html = soup.find_all("table")[meal_idx].find_all('tr')

        menu_json_list = []
        for i in range(len(menu_html)):
            if(i != 0):
                menu_json = {
                "menu":menu_html[i].find_all("th")[0].text.strip(),
                "food":', '.join(menu_html[i].find_all("td")[0].text.strip().split('\r')).strip(),
                "price":menu_html[i].find_all("td")[1].text.strip()}
                menu_json_list.append(menu_json)

        return menu_json_list
        
    
    menu_json_list = parse_menu_json(when, html_doc)
    return makeup_menu(menu_json_list)


def get_hakshik_of(where):
    def get_html_doc(where):
        target_url = url[where]
        res_html = requests.request(url = target_url, method='GET').content

        return res_html
    

    html_doc = get_html_doc(where)
    today = datetime.date.today().strftime("%Y년 %m월 %d일")

    breakfast_json = parse_meal(when='breakfast', html_doc=html_doc)
    lunch_json = parse_meal(when='lunch', html_doc=html_doc)
    dinner_json =parse_meal(when='dinner', html_doc=html_doc)

    hakshik_here = {
        "where":where,
        "breakfast":breakfast_json,
        "lunch":lunch_json,
        "dinner":dinner_json
    }

    hakshik_here = f'{where}\n\n*조식*\n\n{breakfast_json}\n\n*중식*\n\n{lunch_json}\n\n*석식*\n\n{dinner_json}'

    return hakshik_here


def send_message_to_channel(message):
    slack_client = WebClient(token=bot_token)
    slack_client.chat_postMessage(
            channel=channel_id,
            text=message
        )
    
@app_slack.event("message")
def got_message(client, body):
    text = body.get('event').get('text')
    print(text)

    if(text == "안녕"):
        send_message_to_channel("응 안녕")
    elif(text == '오늘 학식'):
        today_hakshik = str(get_hakshik_of('student'))
        send_message_to_channel(today_hakshik)
    elif(text == '오늘 교식'):
        today_hakshik = str(get_hakshik_of('professor'))
        send_message_to_channel(today_hakshik)

@app_slack.event("channel_created")
def channel_created(client, body):
    # Get information about the channel
    channel_id = body["event"]["channel"]["id"]
    channel_name = body["event"]["channel"]["name"]

    # Send a welcome message
    send_message_to_channel(f"Thanks for inviting me to #{channel_name}!")







web = Flask(__name__)
@web.route('/')
def index():
    return render_template('index.html')

@web.route('/gogo')
def gogo():
    get_hakshik_of('professor')
    return redirect(url_for("index"))



if __name__ == "__main__":
    # web.run(debug=True, port='5001')
    SocketModeHandler(app_slack,app_token).start()