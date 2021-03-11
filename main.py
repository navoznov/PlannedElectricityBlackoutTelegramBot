import requests
from lxml import html
import datetime
import options, optionsParser

def get_news_html(region_number: int, begin_date: datetime.datetime, end_date: datetime.datetime):
    # TODO: убрать хардкод дат и региона
    begin_date_str = begin_date.strftime('')
    params_str = f'region={region_number}&district=0&begin_date=09.03.2021&end_date=11.03.2021'
    url = f'https://mrsk-cp.ru/for_consumers/planned_emergency_outages/planned_outages_timetable/get_outages.php?{params_str}'
    response = requests.get(url)
    return response.text


def parse_blackouts(news_html):
    tree = html.fromstring(news_html)
    trs = tree.xpath('//tbody/tr')
    BEGIN_TIME_TD_INDEX = 4
    END_TIME_TD_INDEX = 6
    result = []
    for tr in trs:
        tds = tr.xpath('./td')
        region = tr.xpath('./td[@name="cell-region"]')[0].text
        place = tr.xpath('./td[@id="col-place"]')[0].text
        begin_date_srt = tr.xpath('./td[@id="col-bdate"]')[0].text
        begin_time_str = tds[BEGIN_TIME_TD_INDEX].text
        begin_date = f'{begin_date_srt} {begin_time_str}'
        end_date_str = tr.xpath('./td[@id="col-edate"]')[0].text
        end_time_str = tds[END_TIME_TD_INDEX].text
        end_date = f'{end_date_str} {end_time_str}'

        result.append((region, place, begin_date, end_date))

    return result


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


def send_bot_message(token, chat_id, text):
    params = {'chat_id': chat_id, 'text': text}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, data=params)
        return response
    except Exception as e:
        logging.exception('Ошибка Telegram API sendMessage.')
        return None


def get_blackouts_text_for_output(blackouts):
    max_region_length = max([len(r if r else '') for r,_,_,_ in blackouts])
    max_place_length = max([len(p if p else '') for _,p,_,_ in blackouts])
    lines = []
    for region, place, begin_date, end_date in blackouts:
        region = region if region else ''
        place = place if place else ''
        lines.append(f'{region.ljust(max_region_length)} | {place.ljust(max_place_length)} | {begin_date} | {end_date}')

    return '\n'.join(lines)

options = optionsParser.parse()
bot_token = options.telegram_bot_token
CHECK_BLACKOUT_NEWS_MIN_PERIOD = datetime.timedelta(seconds=10)
CHECK_BOT_UPDATES_MIN_PERIOD = datetime.timedelta(seconds=10)
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
        news_html = get_news_html()
        blackouts = parse_blackouts(news_html)
        last_news_udpate_date = now

    for update in updates:
        message = update.get('message', None)
        if not message:
            continue

        user_text = message.get('text', None)
        if not user_text:
            continue

        chat = message.get('chat', None)
        if not chat:
            continue

        chat_id = chat.get('id', None)
        if not chat_id:
            continue

        blackouts_for_user = [b for b in blackouts if b[0] and  user_text in b[0] or b[1] and user_text in b[1]]
        if blackouts_for_user:
            title = 'Ближайшие отключения:'
            text = title + '\n' + get_blackouts_text_for_output(blackouts_for_user)
        else:
            text = 'В ближайшие несколько дней отключений не предвидется.'
        send_bot_message(bot_token, chat_id, text)
