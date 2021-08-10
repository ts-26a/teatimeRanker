import os
import json
from teatime_ranker.util import float_round, kyui

from .util import authorize, get_root_dir, parse_date, \
                    datetime_today, float_round, average


class User:
    def __init__(self, user_id, api=None, detail=True):
        self.user_id = user_id
        if detail:
            if api is None:
                api = authorize()
            user = api.get_user(user_id)
            self.screen_name = user.screen_name
        user_record_path = f"{get_root_dir()}/data/records/{self.user_id}.json"
        if os.path.exists(user_record_path):
            with open(user_record_path, "r") as f:
                self.__records = json.load(f)
        else:
            self.__records = {
                "win": 0
            }
        self.rating, _ = self.calc_rating()
    
    @property
    def records(self):
        return {d: m for d, m in self.__records.items() if d not in ("win")}
    
    def calc_rating(self, until=None):
        user_record = self.records
        if not user_record:
            return 0, None
        if until is not None:
            r = {}
            for date, ms in user_record.items():
                if date > until:
                    break
                r[date] = ms
            user_record = r
        points = [0] * 10
        today = datetime_today()
        today_perf = 10000 * 2**(-list(user_record.values())[-1]/100)
        for date, ms in user_record.items():
            if (today - parse_date(date)).days <= 15:
                point = 10000 * 2**(-ms/100)
                if len(points) < 10:
                    points.append(float_round(point, "0.00001"))
                if min(points) < point:
                    points = sorted(points)[1:] + [point]
        return average(points), float_round(today_perf, "0.00001")
    
    def update(self, record):
        old_rating = self.rating
        self.__records[record["date"]] = record["ms"]
        if record["rank"] == 1:
            self.__records["win"] += 1
        with open(f"{get_root_dir()}/data/records/{self.user_id}.json", "w") as f:
            json.dump(self.__records, f, indent=4)
        self.rating, today_perf = self.calc_rating()
        print(self.rating, old_rating)
        rating_diff = self.rating - old_rating
        if old_rating < 9500 <= self.rating:
            self.new_ror = True
        return self.rating, today_perf, rating_diff
