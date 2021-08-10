import datetime
import os, os.path
import json
import glob
import time
import textwrap

from .User import User
from .TeatimeTweet import TeatimeTweet
from .Table import Table
from .Graph import Graph
from .util import authorize, average, get_root_dir, str_today, kyui


class Teatime:
    def __init__(self):
        self.api = authorize()
    
    def search_teatime(self):
        today= datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        year, month, day = 2021, 8, 10
        q = textwrap.dedent(f"""\
                "ティータイムですわ" \
                since:{year}-{month:02}-{day:02}_14:59:59_JST \
                until:{year}-{month:02}-{day:02}_15:01:00_JST\
                """)
        result = self.api.search(
            q=q,
            count=200,
            result_type="recent"
        )
        res = []
        for r in result:
            p = TeatimeTweet(r, self.api)
            if p.is_valid_tweet():
                res.append(p)
        return res
    
    def rank_result(self, result):
        result = sorted(result, key=lambda x: x.ms)
        ranking = {}
        i = 0
        p = 1
        prev_ms = None
        for r in result:
            if prev_ms == r.ms:
                p += 1
                ranking[i].append(r)
            else:
                i += p
                p = 1
                ranking[i] = [r]
            prev_ms = r.ms
        return ranking
    
    def update(self, ranked_result):
        res = []
        for rank, r in ranked_result.items():
            for p in r:
                rating, today_perf, rating_diff = p.author.update({
                    "date": p.date,
                    "ms": p.ms,
                    "rank": rank
                })
                res.append({
                    "no": rank,
                    "screen_name": p.author.screen_name,
                    "ms": p.ms,
                    "rating": rating,
                    "diff": rating_diff,
                    "perf": today_perf
                })
        return res

    def result(self):
        search_res = self.search_teatime()
        ranked_res = self.rank_result(search_res)
        res = self.update(ranked_res)
        table = Table(res)
        table.make_table()
        for win_tweet in ranked_res[1]:
            self.api.retweet(win_tweet.id)
        self.api.update_with_media(
            status=f"TEATIME RESULT({str_today()})",
            filename=f"{get_root_dir()}/data/images/{str_today()}.png"
        )
        self.ranking = {k: [x.author.user_id for x in v] for k, v in ranked_res.items()}
        with open(f"{get_root_dir()}/data/records/ranking.json", "w") as f:
            json.dump(self.ranking, f)
    
    def reply_text(self, screen_name, user_id):
        user = User(user_id, detail=False)
        if not user.records:
            return "No data"
        highest = 0
        highest_ms = 1000000
        mses = list(user.records.values())
        latest_7_records = mses[:7]
        min_ms = min(mses)
        max_ms = max(mses)
        ave_ms = average(mses, "0.01")
        for date, ms in user.records.items():
            rating, _ = user.calc_rating(date)
            if highest < rating:
                highest = rating
            if highest_ms > ms:
                highest_ms = ms
        user_kyui = kyui(highest)
        for rank, ids in self.ranking.items():
            for id_ in ids:
                if id_ == user_id:
                    ranking = rank
        number_of_user = len(self.ranking)
        part_games = len(user.records)
        return textwrap.dedent(f"""\
            @{screen_name} \
            {screen_name}
            級位: {user_kyui}
            　最高pt: {highest}
            　現在pt: {user.rating}
            　ランキング: {ranking}/{number_of_user}
            出場試合数: {part_games}
            自己ベスト: {highest_ms}
            min/max/ave: {min_ms}/{max_ms}/{ave_ms}
            直近7記録:
            　{" ".join(str(x) for x in latest_7_records)}
            """)
    
    def reply_result(self, screen_name, user_id, tweet_id):
        reply_text = self.reply_text(screen_name, user_id)
        self.api.update_status(status=reply_text, in_reply_to_status_id=tweet_id)
    
    def __reply(self):
        since_id_file = f"{get_root_dir()}/data/reply"
        with open(since_id_file, "r") as f:
            since_id = f.read() or None
        mentions = self.api.mentions_timeline(since_id=since_id)
        for mention in mentions:
            self.reply_result(mention.user.screen_name, mention.user.id, mention.id_str)
        with open(since_id_file, "w") as f:
            f.write(mention.id_str)
    
    def reply(self):
        for _ in range(50):
            self.__reply()
            time.sleep(12)