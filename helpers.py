import datetime


datetime_format = '%Y-%m-%d %H:%M:%S.%f'
ui_datetime_format = '%Y-%m-%d %H:%M:%S'


def get_numeral_string_form(count: int , one_str: str, two_str: str, five_str: str) -> str:
    '''Метод возвращает строку в падеже взависимости от числа
    Например, вернет "стол" для count=101 (потому что сто один СТОЛ), вернет "стола" для count=23 и тд'''

    remainder = count % 100
    if 10 <= remainder <=19:
        return five_str

    remainder = count % 10
    if remainder == 1:
        return one_str
    elif 2 <= remainder <= 4:
        return two_str
    else:
        return five_str


def get_time_delta_pretty_str(start_date, end_date):
    '''Метод выводит разницу между датами в приличном виде 01:02:12:35'''
    time_delta = end_date - start_date
    if (time_delta.days > 0):
        result = str(time_delta).replace(" days, ", ":").replace(" day, ", ":")
    else:
        result = "0:" + str(time_delta)
    parts = result.split(':')
    parts = ["%02d" % (int(float(x))) for x in parts]
    result = ":".join(parts)
    return result
