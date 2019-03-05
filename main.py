# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
import re

import io
import sys


def get_comment(comment_content):
    return comment_content.replace(' (подробнее в описании по ссылке справа)', '').strip()


def get_password(comment_content):
    result = re.search('Пароль: \w+', comment_content)
    if result:
        result.group()
    else:
        return 'Без пароля'


def get_CSRF(session):
    r = session.get('https://pokeristby.ru/freerolls/raspisanie-frirollov/')

    soup = BeautifulSoup(r.text, 'lxml')
    return soup.find("meta", {"name": "_csrf"})['content']


def get_data(url):
    s = requests.Session()

    CSRF = get_CSRF(s)
    headers = {'X-CSRF-TOKEN': CSRF,
               'Host': 'pokeristby.ru',
               'Connection': 'keep-alive',
               'Content-Length': '331',
               'Origin': 'https://pokeristby.ru',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/66.0.3359.181 Safari/537.36',
               'Content-Type': 'application/json; charset=UTF-8',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'X-Requested-With': 'XMLHttpRequest',
               'Referer': 'https://pokeristby.ru/freerolls/raspisanie-frirollov/',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

    payload = '{"rooms":[11,4,7,59,62,3,8,9,25,66,17,27,54,57,60,6,22,53,40,33],"games":["HOLDEM_NOLIMIT",' \
              '"HOLDEM_POTLIMIT","OMAHA_POTLIMIT","OMAHA_HILOW","OTHER_GAMES"],"payOutTypes":[0,1,2],"options":[' \
              '"IS_DEPOSITED","IS_PASSWORDED","IS_NEEDTICKET","IS_BUYINED","IS_CONDITIONED","IS_NORESTRICTION",' \
              '"IS_PRIVATE"],"daysToDisplay":1,"maxPayout":1000000,"minPayout":0,"displayOrder":"BY_DATE"} '

    data = json.loads(payload)

    r = s.post(url, headers=headers, json=data)

    soup = BeautifulSoup(r.text, 'lxml')
    a = soup.find('div', class_='tbody')
    rows = a.find_all('div', class_='row')

    for row in rows:
        room_title = row.find('div', class_='room-title-value').text.strip()
        game_type = row.find('div', class_='game-type-value').text.strip()
        game_title = row.find('div', class_='game-title').text.strip()
        game_date = row.find('div', class_='game-date').get('data-time').strip()
        price = row.find('div', class_='prise-value').text.strip()

        comment_content = row.find('div', class_='comment-content').text.strip()

        comment = get_comment(comment_content)
        password = get_password(comment_content)

        d = {'room_title': room_title,
             'game_type': game_type,
             'game_title': game_title,
             'game_date': game_date,
             'price': price,
             'comment': comment,
             'password': password}

        print(d)
    # print(r.text)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

    url = 'https://pokeristby.ru/json/freerolls/filter/'
    get_data(url)


if __name__ == '__main__':
    main()
