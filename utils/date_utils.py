import datetime
import time

# 字符串时间转为时间戳
def Changetime(date):
    return time.mktime(date.timetuple())

def get_today():
    """
    今天日期 eg：20180316
    :return:
    """
    return datetime.datetime.now().strftime("%Y%m%d")


def get_yesterday():
    """
    昨天日期 eg：20180315
    :return:
    """
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=-1)
    yesterday = today + delta
    return yesterday.strftime("%Y%m%d")


def get_this_week():
    """
    本周内的日期 eg：['20180316', '20180315', '20180314', '20180313', '20180312']
    :return:
    """
    days = []
    today = datetime.datetime.now()
    n = today.strftime("%w")
    for i in range(int(n)):
        delta = datetime.timedelta(days=-i)
        day = today + delta
        days.append(day.strftime("%Y%m%d"))
    return days


def get_last_week():
    pass


def get_this_month():
    """
    本月内的日期
    eg:['20180316', '20180315', '20180314', '20180313', '20180312', '20180311', '20180310', '20180309',
    '20180308', '20180307', '20180306', '20180305', '20180304', '20180303', '20180302', '20180301']
    :return:
    """
    days = []
    today = datetime.datetime.now()
    n = today.strftime("%d")
    for i in range(int(n)):
        delta = datetime.timedelta(days=-i)
        day = today + delta
        days.append(day.strftime("%Y%m%d"))
    return days


if __name__ == "__main__":
    print(get_today())
    print(get_yesterday())
    print(get_this_week())
    print(get_this_month())