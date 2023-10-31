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
from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_text_to_fp
import pdfminer.layout
import io
import PyPDF2
from reportlab.pdfgen import canvas
#import fitz
import tabula
import numpy as np
import pandas as pd
import re



app_slack = App(token=app_token)
slack_client = WebClient(token=bot_token)


def parse_meal(when, html_doc, where):
    def makeup_menu(target_json):
        res_arr = []
        for json in target_json:
            res_arr.append(f'[{json.get("menu")}({json["price"]})]\n{json["food"]}')
        return '\n\n'.join(res_arr)
    
    def parse_meal_idx(when, where):
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
        
        if(where=="professor"):
            when_idx = 0
        
        
        return 4*day_of_week_idx + when_idx
    
    
    def parse_menu_json(when, html_doc):
        meal_idx = parse_meal_idx(when, where)
        soup = BeautifulSoup(html_doc, "html.parser", from_encoding='utf-8')
        print(len(soup.find_all("table")))
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

def get_html_doc(where):
        target_url = url[where]
        res_html = requests.request(url = target_url, method='GET').content

        return res_html
def get_hakshik_of(where):
    
    

    html_doc = get_html_doc(where)
    today = datetime.date.today().strftime("%Y년 %m월 %d일")

    breakfast_json = parse_meal(when='breakfast', html_doc=html_doc, where=where)
    lunch_json = parse_meal(when='lunch', html_doc=html_doc, where=where)
    dinner_json =parse_meal(when='dinner', html_doc=html_doc, where=where)

    hakshik_here = {
        "where":where,
        "breakfast":breakfast_json,
        "lunch":lunch_json,
        "dinner":dinner_json
    }
    if(where == "professor"):
        hakshik_here = f'교직원식당 메뉴\n\n{breakfast_json}'
    elif(where == "student"):
        hakshik_here = f'학생식당 메뉴\n\n*조식*\n\n{breakfast_json}\n\n*중식*\n\n{lunch_json}\n\n*석식*\n\n{dinner_json}'

    return hakshik_here


def send_message_to_channel(message):
    slack_client = WebClient(token=bot_token)
    slack_client.chat_postMessage(
            channel=channel_id,
            text=message
        )

def download_pdf(url, path):
    response = requests.get(url)
    with open(path, 'wb') as file:
        file.write(response.content)

def pdf_to_html(pdf_path):

    print("GOGO")
   # try:
   #     text = extract_text(pdf_path)
   #     print(text)
   #     return text
   # except Exception as e:
   #    print(f"Error extracting text from PDF: {str(e)}")
   #    return None
   # Open a file-like object for writing the extracted textf
    laout_parameter = pdfminer.layout.LAParams(boxes_flow=-1, detect_vertical=True,word_margin=2, char_margin=2.0, line_margin=0.1, line_overlap=0.1,  all_texts=True)
    output_file = io.BytesIO()
    # with open('output.html', 'w', encoding='utf-8') as output_file:
    # Extract text from the PDF and write it to the file-like object
    with open(pdf_path, 'rb') as pdf_file:
        extract_text_to_fp(pdf_file, output_file,layoutmode='loose', output_type="html", codec='utf-8', laparams=laout_parameter, disable_caching=True)
    
    data = output_file.getvalue().decode('utf-8')
    with open('./templates/gogo.html','w') as out_file:
        out_file.write(data)
    
    return data


def draw_box_to_pdf(pdf_path):
    def parse_arr_from_df_col(df_col):
        data_list = df_col.tolist()
        filtered_list = [str(word) for word in data_list if type(word) != type(0.0) or type(word) != type("0")]
        return filtered_list
    def makeup_string(target_str):
        target_str = target_str.replace('\n', ', ')
        target_str = target_str.replace('nan', "")
        target_str = target_str.replace("r'(?<=\D)(?=\d{3}\b)'", "")
        return target_str
    def parse_meal_json_of_today(today_array):
        seperator = r'\d\d\d'
        array_splited = split_arr(today_arr, seperator)
        return array_splited
        meal_json = {
            "breakfast":"", "lunch":"", "dinner":"", "easy_meal":""
        }
        
        breakfast = array_splited[0]
        array_splited = array_splited[1:]
        meal_json['breakfast'] = makeup_string(breakfast)

        easy_meal = array_splited[-1]
        array_splited = array_splited[:-2]
        meal_json['easy_meal'] = makeup_string(easy_meal)

        dinner = array_splited[-1]
        array_splited = array_splited[:-2]
        meal_json['easy_meal'] = makeup_string(easy_meal)

    def replace_separator(before, after, array):
        new_list = [before if word == after else word for word in array]
        return new_list
    def replace_word_in_array(before, array):
        replace_separator(before, "|", array)
    def split_arr(array_to_splite, seperator):
        text = '\n'.join(array_to_splite)
        # sublists = text.split(seperator)
        sublists = re.sub(seperator,"|", text)
        sublists = sublists.split("|")
        return text
    def is_nan(target_str):
        if(target_str[:-3] == "nan"):
            return True
        else:
            return False

    # pdf_document = fitz.open(pdf_path)

    # # Create a new PDF document
    # new_pdf = fitz.open()
    
    # for page_number in range(len(pdf_document)):
    #     page = pdf_document[page_number]
        
    #     # Create a new page in the new PDF documenlt with the same size
    #     width, height = 1920, 1080
    #     new_page = new_pdf.new_page(width=width, height=height)
        
    #     # Get the text objects on the page
    #     text_objects = page.get_text("list")
    #     # Iterate through the text objects
    #     for text_obj in text_objects:
    #         print(text_obj)
    #         if 'NEW' not in text_obj['text']:  # Check if the text does not contain "NEW"
    #             new_page.insert_text(text_obj['bbox'], text_obj['text'], fontsize=12)  # Insert the text to the new page
        

        
    
    # Save the new PDF
    # new_pdf.save('./output.pdf')
    # new_pdf.close()

    # dfs = tabula.read_pdf(
	# "./gishiks/gishik_2023-10-2.pdf", 
	# pages="all"
    # )
    dfs = tabula.read_pdf("./gishiks/gishik_2023-10-2.pdf", pages="all", encoding='utf-8')
    # print(f"Data Type :{type(dfs)}")
    # print(f"Data Length: {len(dfs)}")
    # for index, table in enumerate(dfs):
    #   print(f"\nData Index: {index}")
    #   print(type(table))
    #   print(table.head())
    dataframes = []
    for table in dfs:
        df = pd.DataFrame(table)
        # df = df.replace('NaN', np.nan)  # Replace 'NaN' with actual NaN values
        # df = df.dropna(subset=df.columns)
        dataframes.append(df)
    
    n = 6
    column_name = df.columns[n]
    column_data = df[column_name]
    today_arr = parse_arr_from_df_col(column_data)
    today_meal_json = parse_meal_json_of_today(today_arr)
    print(today_meal_json)
        








def parse_today_gishik():
    data =pdf_to_html('./gishiks/gishik_2023-10.pdf')
    soup = BeautifulSoup(str(data), "html.parser", from_encoding='utf-8')
    # today = soup.select_one("body > div:nth-child(8)").text
    today = soup.find_all("text")
    inner_text = '&'.join(soup.stripped_strings)
    print(inner_text.split('&'))
    
def gogo_gishik():
    html = get_html_doc('dormitory')
    soup = BeautifulSoup(html, "html.parser", from_encoding='utf-8')
    this_week_page = soup.find('a', class_='artclLinkView')
    query = this_week_page['href']
    url = f'https://dorm.inha.ac.kr/{query}'

    pdfpage_html =  requests.request(url = url, method='GET').content
    soup = BeautifulSoup(pdfpage_html,  "html.parser", from_encoding='utf-8')
    pdf_url = soup.select_one("body > div > div.artclItem.viewForm > dl > dd > ul > li:nth-child(1) > a")['href']
    url = f'https://dorm.inha.ac.kr/{pdf_url}'
    
    path_to_save_pdf = f'./gishiks/{datetime.date.today().strftime("gishik_%Y-%m-%w")}.pdf'
    download_pdf(url, path_to_save_pdf)
    print(url)

    
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
    elif(text == '오늘 기식'):
        today_gishik = gogo_gishik()
        send_message_to_channel(today_gishik)

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
    pdf_to_html('./gishiks/gishik_2023-10.pdf')
    return redirect(url_for("index"))

@web.get('/html')
def html():
    draw_box_to_pdf('./gishiks/gishik_2023-10-2.pdf')
    return render_template('gogo.html')



if __name__ == "__main__":
    draw_box_to_pdf('./gishiks/gishik_2023-10-2.pdf')
    #web.run(debug=True, port='5001')
    
    #SocketModeHandler(app_slack,app_token).start()