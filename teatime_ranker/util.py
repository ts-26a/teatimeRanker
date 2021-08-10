import datetime
from decimal import Decimal, ROUND_HALF_UP
import os

from dotenv import load_dotenv

import tweepy


def get_root_dir():
    current_dir = os.path.dirname(__file__).replace(os.sep, "/")
    root_dir = "/".join(current_dir.split("/")[:-1])
    return root_dir


load_dotenv(f"{get_root_dir()}/.env")


def float_round(f, t):
    return float(Decimal(str(f)).quantize(Decimal(t), rounding=ROUND_HALF_UP))


def authorize():
    CS_TOKEN = os.environ.get("CS_TOKEN")
    CS_SECRET = os.environ.get("CS_SECRET")
    AC_TOKEN = os.environ.get("AC_TOKEN")
    AC_SECRET = os.environ.get("AC_SECRET")
    auth = tweepy.OAuthHandler(CS_TOKEN, CS_SECRET)
    if AC_TOKEN and AC_SECRET:
        auth.set_access_token(AC_TOKEN, AC_SECRET)
        return tweepy.API(auth)
    print(auth.get_authorization_url())
    verifier = input("Enter the verifier code: ")
    AC_TOKEN, AC_SECRET = auth.get_access_token(verifier)
    with open(".env", "r+") as f:
        f.write("\n".join(
            f.read().split("\n")[:2] + [f"{AC_TOKEN=}", f"{AC_SECRET=}"]
        ))
    return tweepy.API(auth)


def twid_to_ms(twid):
    unix_time = ((int(twid) >> 22) + 1288834974657) / 1000
    return int(datetime.datetime.fromtimestamp(unix_time).strftime("%S%f"))


def average(ls, t="0.00001"):
    return float_round(sum(ls) / len(ls), t)



def dict_sort(dic, key=lambda x: x[1]):
    return dict(sorted(dic.items(), key=key))


def datetime_today():
    date_today = datetime.date.today()
    year = date_today.year
    month = date_today.month
    day = date_today.day
    return datetime.datetime(year, month, day)


def str_today():
    return datetime_today().strftime("%Y-%m-%d")


def parse_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d")


def pretty_float(f):
    f = float(f)
    if f.is_integer():
        return int(f)
    return f


def rating_colors(rating):
    if 9500 <= rating:
        return "#FF8282"
    if 9000 <= rating < 9500:
        return "#FFAB57"
    if 8000 <= rating < 9000:
        return "#FFFF99"
    if 7000 <= rating < 8000:
        return "#6363FF"
    if 6000 <= rating < 7000:
        return "#7AFFFF"
    if 4000 <= rating < 6000:
        return "#85FF85"
    if 2000 <= rating < 4000:
        return "#C98744"
    return "#B3B3B3"

def kyui(rating):
    if 9500 <= rating:
        return "RoR"
    if 9000 <= rating < 9500:
        return "S9"
    if 8500 <= rating < 9000:
        return "S8"
    if 8000 <= rating < 8500:
        return "S7"
    if 7500 <= rating < 8000:
        return "S6"
    if 7000 <= rating < 7500:
        return "S5"
    if 6500 <= rating < 7000:
        return "S4"
    if 6000 <= rating < 6500:
        return "S3"
    if 5500 <= rating < 6000:
        return "S2"
    if 5000 <= rating < 5500:
        return "S1"
    if 4500 <= rating < 5000:
        return "A+"
    if 4000 <= rating < 4500:
        return "A"
    if 3500 <= rating < 4000:
        return "B+"
    if 3000 <= rating < 3500:
        return "B"
    if 2500 <= rating < 3000:
        return "C+"
    if 2000 <= rating < 2500:
        return "C"
    if 1500 <= rating < 2000:
        return "D+"
    if 1000 <= rating < 1500:
        return "E+"
    return "E"