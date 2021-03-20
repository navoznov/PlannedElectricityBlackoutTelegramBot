#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from lxml import html
import datetime
import options, optionsParser
from blackout import Blackout


def get_news_html(region_number: int, begin_date: datetime.datetime, end_date: datetime.datetime):
    DATE_FORMAT = '%d.%m.%Y'
    begin_date_str = begin_date.strftime(DATE_FORMAT)
    end_date_str = end_date.strftime(DATE_FORMAT)
    params_str = f'region={region_number}&district=0&begin_date={begin_date_str}&end_date={end_date_str}'
    url = f'https://mrsk-cp.ru/for_consumers/planned_emergency_outages/planned_outages_timetable/get_outages.php?{params_str}'
    response = requests.get(url)
    return response.text


def parse_blackouts(news_html: str):
    tree = html.fromstring(news_html)
    trs = tree.xpath('//tbody/tr')
    BEGIN_TIME_TD_INDEX = 4
    END_TIME_TD_INDEX = 6
    result = []
    for tr in trs:
        tds = tr.xpath('./td')
        district = tr.xpath('./td[@name="cell-region"]')[0].text
        place = tr.xpath('./td[@id="col-place"]')[0].text
        address = tr.xpath('./td[@id="col-address"]')[0].text
        begin_date_srt = tr.xpath('./td[@id="col-bdate"]')[0].text
        begin_time_str = tds[BEGIN_TIME_TD_INDEX].text
        begin_date = f'{begin_date_srt} {begin_time_str}'
        end_date_str = tr.xpath('./td[@id="col-edate"]')[0].text
        end_time_str = tds[END_TIME_TD_INDEX].text
        end_date = f'{end_date_str} {end_time_str}'
        blackout = Blackout(district, place, address, begin_date, end_date)
        result.append(blackout)

    return result


def get_blackouts(region_number: int, begin_date: datetime.datetime, end_date: datetime.datetime):
    news_html = get_news_html(region_number, searching_begin_date, searching_end_date)
    return parse_blackouts(news_html)

def get_bot_updates(token, offset):
    params = {'timeout': 30, 'offset': offset}
    response_json = {}
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(url, params)
        response_json = response.json()
    except Exception as e:
        logging.exception('Ошибка Telegram API getUpdates.')

    return response_json.get('result', [])


def get_message_chat_id(message):
    chat = message.get('chat', None)
    return chat.get('id', None) if chat else None


def send_bot_message(token, chat_id, text):
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, data=params)
        return response
    except Exception as e:
        logging.exception('Ошибка Telegram API sendMessage.')
        return None


def filter_blackouts(blackouts, text: str):
    return [b for b in blackouts if b.district and text in b.district or b.place and text in b.place]


def blackout_to_output_string(blackout, max_district_length, max_place_length):
    district = blackout.district if blackout.district else ''
    place = blackout.place if blackout.place else ''
    return f'{district.ljust(max_district_length)} | {place.ljust(max_place_length)} | {blackout.begin_date} - {blackout.end_date}'


def get_blackouts_text_for_output(blackouts):
    max_district_length = max([len(b.district if b.district else '') for b in blackouts])
    max_place_length = max([len(b.place if b.place else '') for b in blackouts])
    lines = [blackout_to_output_string(b, max_district_length, max_place_length) for b in blackouts]
    return '\n'.join(lines)


def is_need_to_update_blackout_news(last_udpate_date):
    last_udpate_time = last_udpate_date.time()
    CHECK_BLACKOUT_NEWS_TIMES = [datetime.time(10), datetime.time(15), datetime.time(20)]
    now_time = datetime.datetime.now().time()
    result = False
    for time in CHECK_BLACKOUT_NEWS_TIMES:
        if not is_near_time(last_udpate_time, time) and is_near_time(now_time, time):
            return True
    return False


def is_near_time(source_time, target_time, delta = datetime.timedelta(minutes=5)):
    return target_time - delta < source_time < target_time + delta


region_number = 43
options = optionsParser.parse()
bot_token = options.telegram_bot_token
CHECK_BLACKOUT_NEWS_MIN_PERIOD = datetime.timedelta(seconds=10)
CHECK_BOT_UPDATES_MIN_PERIOD = datetime.timedelta(seconds=10)
NEWS_SEARCHING_PERIOD_IN_DAYS = 3
news_searching_period = datetime.timedelta(days=NEWS_SEARCHING_PERIOD_IN_DAYS)
# todo: переименовать
last_update_id = 0
blackouts = []
last_news_udpate_date = datetime.datetime.now() - datetime.timedelta(days=3)
last_bot_udpates_checking_date = datetime.datetime.now() - datetime.timedelta(days=3)
while True:
    now = datetime.datetime.now()
    if now < last_bot_udpates_checking_date + CHECK_BOT_UPDATES_MIN_PERIOD:
        continue

    offset = last_update_id + 1
    updates = get_bot_updates(bot_token, offset)
    last_bot_udpates_checking_date = now
    if len(updates) == 0:
        continue

    update_ids = [update['update_id'] for update in updates]
    last_update_id = max(update_ids)

    if now > last_news_udpate_date + CHECK_BLACKOUT_NEWS_MIN_PERIOD:
        searching_begin_date = now.date()
        searching_end_date = (now + news_searching_period).date()

        try:
            blackouts = get_blackouts(region_number, searching_begin_date, searching_end_date)
            last_news_udpate_date = now
        except:
            # TODO: Обработка ошибки
            continue

    for update in updates:
        message = update.get('message', None)
        if not message:
            continue

        user_text = message.get('text', None)
        if not user_text:
            continue

        chat_id = get_message_chat_id(message)
        if not chat_id:
            continue

        blackouts_for_user = filter_blackouts(blackouts, user_text)
        if blackouts_for_user:
            title = 'Ближайшие отключения:'
            text = title + '\n' + '```\n' + get_blackouts_text_for_output(blackouts_for_user) + '```'
        else:
            text = 'В ближайшие несколько дней отключений не предвидется.'
        send_bot_message(bot_token, chat_id, text)
