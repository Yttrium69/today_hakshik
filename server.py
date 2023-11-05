from flask import Flask, render_template, jsonify, redirect, url_for, request
import requests
# import time
from config import app_token, bot_token, channel_id, url
# from slack_bolt import App
# from slack_bolt.adapter.socket_mode import SocketModeHandler
# from slack_sdk import WebClient
import bs4
import datetime
from pytz import timezone
import json
# from pdfminer.high_level import extract_text
# from pdfminer.high_level import extract_text_to_fp
# import pdfminer.layout
# import io
# import PyPDF2
# from reportlab.pdfgen import canvas
# import fitz
import tabula
# import numpy as np
# import pandas as pd
import pandas as pd
import re
# C:\Users\dudal\OneDrive\바탕 화면 1\today_hakshik\modules_for_hakshikking_update\python

# app_slack = App(token=app_token)
# slack_client = WebClient(token=bot_token)


class Shik_thisweek:
    data = {}
    where = ""

    def __init__(self) -> None:
        pass

    def save_my_data(self):
        with open(f'./meal_data/{self.where}.json', 'w', encoding='UTF-8') as f:
            json.dump(self.data, f, ensure_ascii=False)

    def set_shik(self, data):
        self.data = data

    def get_shik(self, when):
        if (when == "all"):
            return self.data
        else:
            return self.data[when]

    def get_html_doc(self, where):
        target_url = url[where]
        res_html = requests.request(url=target_url, method='GET').content

        return res_html


class Gishik_thisweek(Shik_thisweek):
    where = "dimitory"

    def __init__(self):
        super().__init__()

    def update_me(self):
        self.data = self.get_gishik_json_of_this_week()
        self.save_my_data()

    def get_gishik_json_of_this_week(self):
        pdf_path = self.get_gishik_pdf()
        this_week_json = self.parse_this_week_json(pdf_path)
        return this_week_json

    def get_gishik_pdf(self):
        def download_pdf(url, path):
            response = requests.get(url)
            with open(path, 'wb') as file:
                file.write(response.content)

        html = self.get_html_doc('dormitory')
        soup = bs4.BeautifulSoup(html, "html.parser", from_encoding='utf-8')
        this_week_page = soup.find('a', class_='artclLinkView')
        query = this_week_page['href']
        url = f'https://dorm.inha.ac.kr/{query}'

        pdfpage_html = requests.request(url=url, method='GET').content
        soup = bs4.BeautifulSoup(pdfpage_html,  "html.parser",
                                 from_encoding='utf-8')
        pdf_url = soup.select_one(
            "body > div > div.artclItem.viewForm > dl > dd > ul > li:nth-child(1) > a")['href']
        url = f'https://dorm.inha.ac.kr/{pdf_url}'

        path_to_save_pdf = f'./gishiks/{datetime.date.today().strftime("gishik_%Y-%m-%S")}.pdf'
        download_pdf(url, path_to_save_pdf)

        return path_to_save_pdf

    def parse_this_week_json(self, pdf_path):
        def parse_arr_from_df_col(df_col):
            data_list = df_col.tolist()
            filtered_list = [str(word) for word in data_list if type(
                word) != type(0.0) or type(word) != type("0")]
            return filtered_list

        def makeup_string(target_str):
            target_str = target_str.replace('\n', ' ')
            target_str = target_str.replace('\r', ', ')
            target_str = target_str.replace('nan', "")
            target_str = target_str.replace('일품식', "\n일품식")
            target_str = target_str.replace('요청', "")
            target_str = target_str.replace('NEW', "")
            target_str = target_str.replace("r'(?<=\D)(?=\d{3}\b)'", "")
            target_str = target_str.replace("self 라면", "")
            target_str = target_str.replace("라면/밥/김치", "")
            target_str = target_str.replace("한 식 ", "한식\n")
            return target_str

        def replace_separator(before, after, array):
            new_list = [before if word == after else word for word in array]
            return new_list

        def replace_word_in_array(before, array):
            replace_separator(before, "|", array)

        def correct_arr(array_to_splite):
            seperator = r'\d{2,}'
            text = '\n'.join(array_to_splite)
            # sublists = text.split(seperator)
            sublists = re.sub(seperator, "|", text)
            # sublists = re.sub(r"\nnan*", "|", text)
            sublists = sublists.replace("\nnan\nnan\nnan\nnan\nnan", "|")
            sublists = sublists.replace("\nnan\nnan", "|")
            sublists = sublists.split("|")
            sublists = [item for item in sublists if item != ""]
            sublists = [item for item in sublists if 5 < len(item)]
            # array_to_splite = [item for item in array_to_splite if '\r' in item]
            return sublists

        def is_nan(target_str):
            nan_cnt = 0
            target_arr = target_str.split("\n")
            for element in target_arr:
                if "nan" in element and element != "":
                    return False
            return True

        def is_easy_meal_nono(target_array):
            # nan_cnt = target_array[-1].count("nan")
            # if (3 < nan_cnt):
            #     return True
            # else:
            #     return False
            indicator = target_array[-4]
            if (target_array[-4] == "nan" or target_array[-4] == r'\d{2,}'):
                return True
            else:
                return False

        def parse_meal_json_of_today(today_array):
            today_arr = today_array

            meal_json = {
                "breakfast": "", "lunch": "", "dinner": "", "easy_meal": ""
            }
            is_easy_meal_nono_flag = is_easy_meal_nono(today_arr)

            corrected_arr = correct_arr(today_arr)
            if (len(corrected_arr) == 0 or corrected_arr == None):
                print("데이터 없음")
                return "데이터 없음"

            easy_meal = ""
            if (is_easy_meal_nono_flag == True):
                meal_json['easy_meal'] = "X"
                # easy_meal = corrected_arr[-1]
                # corrected_arr = corrected_arr[:-1]
            else:
                easy_meal = corrected_arr[-1]
                corrected_arr = corrected_arr[:-1]
                meal_json['easy_meal'] = makeup_string(easy_meal)

            breakfast = corrected_arr[0]
            corrected_arr = corrected_arr[1:]
            meal_json['breakfast'] = makeup_string(breakfast)

            dinner = corrected_arr[-1]
            corrected_arr = corrected_arr[:-1]
            meal_json['dinner'] = makeup_string(dinner)

            lunch = '\n\n'.join(corrected_arr)
            meal_json['lunch'] = makeup_string(lunch)

            return meal_json

        def pdf_to_df(pdf_path):
            col_names = ["blank", "Monday", "Tuesday", "Wednesday",
                         "Thursday", "Friday", "Saturday", "Sunday"]
            dfs = tabula.read_pdf(pdf_path,
                                  pages="all", encoding='utf-8', lattice=True)
            dataframes = [pd.DataFrame(table) for table in dfs]
            merged_df = pd.concat(dataframes, axis=1)
            return merged_df

        this_week_json_dict = {"Monday": "", "Tuesday": "", "Wednesday": "",
                               "Thursday": "", "Friday": "", "Saturday": "", "Sunday": ""}
        df = pdf_to_df(pdf_path)
        for idx, today in enumerate(["-1", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
            if (idx != 0):
                column_name = df.columns[idx]
                column_data = df[column_name]
                today_arr = parse_arr_from_df_col(column_data)
                today_meal_json = parse_meal_json_of_today(today_arr)
                this_week_json_dict[today] = today_meal_json
        return this_week_json_dict

    # def get_today_gishik(self):
    #     day_of_this_week = datetime.now().strftime("%A")
    #     this_week_json = self.get_gishik_json_of_this_week()
    #     today_json =
    #     print(day_of_this_week)


class Hakshik_thisweek(Shik_thisweek):
    where = "student"

    def __init__(self):
        super().__init__()

    def update_me(self):
        self.data = self.get_hakshik_json_of_this_week()
        self.save_my_data()

    def get_hakshik_json_of_this_week(self):
        this_week_json_dict = {"Monday": "", "Tuesday": "", "Wednesday": "",
                               "Thursday": "", "Friday": "", "Saturday": "", "Sunday": ""}
        for today in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            today_json = self.get_today_hakshik(self.where, today)
            this_week_json_dict[today] = today_json
        return this_week_json_dict

    def parse_meal_json_today(self, when, html_doc, where, weekday):
        def makeup_menu(target_json):
            res_arr = []
            for json in target_json:
                res_arr.append(
                    f'[{json.get("menu")}({json["price"]})]\n{json["food"]}')
            return '\n\n'.join(res_arr)

        def parse_meal_idx(when, where, weekday):
            day_of_week_idx = -1
            when_idx = -1
            # day_of_week_idx = datetime.date.today().weekday()

            if (weekday == "Monday"):
                day_of_week_idx = 0
            if (weekday == "Tuesday"):
                day_of_week_idx = 1
            if (weekday == "Wednesday"):
                day_of_week_idx = 2
            if (weekday == "Thursday"):
                day_of_week_idx = 3
            if (weekday == "Friday"):
                day_of_week_idx = 4

            if (when == 'breakfast'):
                when_idx = 0
            elif (when == 'lunch'):
                when_idx = 1
            elif (when == 'self'):
                when_idx = 2
            elif (when == 'dinner'):
                when_idx = 3

            res = 0

            if (where == "professor"):
                res = day_of_week_idx
            else:
                res = 4*day_of_week_idx + when_idx

            return res

        def parse_menu_json(when, html_doc):
            meal_idx = parse_meal_idx(when, where, weekday)
            soup = bs4.BeautifulSoup(html_doc, "html.parser",
                                     from_encoding='utf-8')
            menu_html = soup.find_all("table")[meal_idx].find_all('tr')

            menu_json_list = []
            for i in range(len(menu_html)):
                if (i != 0):
                    menu_json = {
                        "menu": menu_html[i].find_all("th")[0].text.strip(),
                        "food": ', '.join(menu_html[i].find_all("td")[0].text.strip().split('\r')).strip(),
                        "price": menu_html[i].find_all("td")[1].text.strip()}
                    menu_json_list.append(menu_json)

            return menu_json_list

        menu_json_list = parse_menu_json(when, html_doc)
        return makeup_menu(menu_json_list)

    def get_today_hakshik(self, where, weekday):
        html_doc = self.get_html_doc(where)

        breakfast_json = self.parse_meal_json_today(
            when='breakfast', html_doc=html_doc, where=where, weekday=weekday)
        lunch_json = self.parse_meal_json_today(
            when='lunch', html_doc=html_doc, where=where, weekday=weekday)
        dinner_json = self.parse_meal_json_today(
            when='dinner', html_doc=html_doc, where=where, weekday=weekday)

        hakshik_here = {
            "breakfast": breakfast_json,
            "lunch": lunch_json,
            "dinner": dinner_json
        }
        return hakshik_here


class Gyoshik_thisweek(Hakshik_thisweek):
    where = "professor"

    def __init__(self):
        super().__init__()
        self.data = self.get_hakshik_json_of_this_week()


def program_init():
    global gyoshik_week_instance
    global gishik_week_instance
    global hakshik_week_instance

    gyoshik_week_instance = Gyoshik_thisweek()
    gyoshik_week_instance.update_me()
    gishik_week_instance = Gishik_thisweek()
    gishik_week_instance.update_me()
    hakshik_week_instance = Hakshik_thisweek()
    hakshik_week_instance.update_me()

    print("GOGO")

    updated_json = get_week()
    return parse_json_to_message_week(updated_json)


def this_weekday():
    return datetime.datetime.now(timezone('Asia/Seoul')).strftime("%A")


def today():
    return datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y년 %m월 %d일")


def parse_json_to_message(json_data, today_of_week):
    json_data = json_data.replace("'", '"')
    json_data = json.loads(json_data)
    today_hak = json_data['hak'].get(today_of_week)
    today_gyo = json_data['gyo'].get(today_of_week)
    today_gi = json_data['gi'].get(today_of_week)

    if (today_hak != ''):
        hak_message = f'*학생식당*\n\n✨ 조식 ✨\n{today_hak["breakfast"]}\n\n☀ 중식 ☀\n{today_hak["lunch"]}\n\n🌙 석식 🌙\n{today_hak["dinner"]}\n\n\n'
    else:
        hak_message = f'*학생식당*\n식사를 제공하지 않는 날입니다.\n'
    if (today_gyo != ''):
        today_gyo = today_gyo.get('breakfast').replace("\t\t", "").split('\n')
        today_gyo = [item for item in today_gyo if item != ""]
        gyo_message = f'*교직원식당*\n\n✨ 조식 ✨\n{today_gyo[0]}\n{today_gyo[1]}\n\n☀ 중식 ☀\n{today_gyo[2]}\n(백반)\n{today_gyo[3]}\n\n(특식)\n{today_gyo[5]}\n\n\n🌙 석식 🌙\n{today_gyo[6]}\n{today_gyo[7]}\n\n\n'
    else:
        gyo_message = f'*교직원식당*\n식사를 제공하지 않는 날입니다.\n'
    if (today_gi != ''):
        gi_message = f'*생활관식당*\n\n✨ 조식 ✨\n{today_gi["breakfast"]}\n\n☀ 중식 ☀\n{today_gi["lunch"]}\n\n🌙 석식 🌙\n{today_gi["dinner"]}\n\n🌭 간편식 🌭\n{today_gi["easy_meal"]}\n\n\n'
    else:
        gi_message = f'*생활관식당*\n식사를 제공하지 않는 날입니다.\n'
    return f'✉ 학식왕 김인하 - {today()} 식단 ✉\n\n\n{hak_message}\n{gyo_message}\n{gi_message}식사 맛있게 하세요!'


def parse_json_to_message_week(json_data):
    week_message = []
    for today_of_week in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        today_message = parse_json_to_message(json_data, today_of_week)
        week_message.append(today_message)
    return '\n\n\n\n--------------\n\n\n\n'.join(week_message)


web = Flask(__name__)
web.config['JSON_AS_ASCII'] = False


@web.get('/')
def index():
    return "GOGO"


@web.get('/init')
def init():
    res = program_init()
    return res


@web.get('/get')
def get_week():
    where = request.args.get('where')
    data = "ERROR"
    if (where == "hak"):
        data = hakshik_week_instance.get_shik(when="all")
    elif (where == "gi"):
        data = gishik_week_instance.get_shik(when="all")
    elif (where == "gyo"):
        data = gyoshik_week_instance.get_shik(when="all")
    else:
        data = {"hak": hakshik_week_instance.get_shik(when="all"), "gi":
                gishik_week_instance.get_shik(when="all"), "gyo": gyoshik_week_instance.get_shik(when="all")}
        # data = get_week()
    data = str(data)
    return data


if __name__ == "__main__":
    web.run("0.0.0.0", port=5000, debug=False)
