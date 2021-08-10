from datetime import timedelta

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from .User import User
from .util import get_root_dir, parse_date, rating_colors

class Graph:
    def __init__(self, user_id):
        self.user = User(user_id)
        fe = fm.FontEntry(
            fname=f"{get_root_dir()}/data/fonts/mgenplus-1cp-regular.ttf",
            name="Mgen+ 1cp Regular"
        )
        fm.fontManager.ttflist = [fe]
        mpl.rcParams["font.family"] = "Mgen+ 1cp Regular"
    
    def __dateFormatter(self, ax, max_date, min_date):
        month_delta = (max_date.year - min_date.year) * 12 + \
            max_date.month - min_date.month
        day_delta = (max_date - min_date).days
        if month_delta >= 12:
            months = mdates.MonthLocator()
            ax.xaxis.set_major_locator(months)
            def dateFormatter(x, _):
                dt_ = mdates.num2date(x).replace(tzinfo=None)
                year = month = ""
                if (dt_.month == 1 or
                        (dt_.month == min_date.month + 1 and dt_.year == min_date.year)):
                    year = dt_.year
                if (dt_.month % 3 == 1 or 
                        (dt_.month == min_date.month and dt_.year == min_date.year)):
                    month = dt_.month
                    month = f"{month:01}"
                if year:
                    return f"{year}/{month}"
                return month
        elif month_delta >= 2:
            months = mdates.MonthLocator()
            ax.xaxis.set_major_locator(months)
            def dateFormatter(x, _):
                dt_ = mdates.num2date(x).replace(tzinfo=None)
                month = dt_.month
                year = ""
                if (dt_.month == 1 or
                        (dt_.month == min_date.month + 1 and dt_.year == min_date.year)):
                    year = dt_.year
                if year:
                    return f"{year}/{month}"
                return month
        else:
            days = mdates.DayLocator()
            ax.xaxis.set_major_locator(days)
            def dateFormatter(x, _):
                dt_ = mdates.num2date(x).replace(tzinfo=None)
                if day_delta > 10:
                    interval = 5
                else:
                    interval = 1
                month = ""
                day = ""
                if ((dt_.day == 1) or ((dt_ - min_date).days <= (interval - 1)) and
                        day != ""):
                    month = dt_.month
                    month = f"{month:01}"
                if (not (dt_.day - 1) % interval and
                        (dt_ + timedelta(days=interval-1)).month == dt_.month):
                    day = dt_.day
                    day = f"{day:01}"
                if month:
                    return f"{month}/{day}"
                return day
        return dateFormatter
    
    def make_graph(self):
        if not self.user.records:
            return "No data"
        dates = self.user.records.keys()
        min_date = parse_date(min(dates))
        max_date = parse_date(max(dates))
        perf_x = []
        perf_y = []
        perf_color = []
        rating_x = []
        rating_y = []
        rating_color = []
        for date in dates:
            parsed_date = parse_date(date)
            rating, perf = self.user.calc_rating(date)
            perf_x.append(parsed_date)
            perf_y.append(perf)
            perf_color.append(rating_colors(perf))
            rating_x.append(parse_date(date))
            rating_y.append(rating)
            rating_color.append(rating_colors(rating))
        fig, ax = plt.subplots()
        days_4 = timedelta(days=3)
        min_rating = int(min(rating_y))
        max_rating = int(max(rating_y))
        min_perf = int(min(perf_y))
        max_perf = int(max(perf_y))
        if min_rating < 1000:
            y_rmin = 0
        else:
            y_rmin = int(f"{int(str(min_rating)[0])-1}000")
        if max_rating == 10000:
            y_rmax = 10000
        else:
            y_rmax = int(f"{int(str(max_rating)[0])+1}000")
        if min_perf < 1000:
            y_pmin = 0
        else:
            y_pmin = int(f"{int(str(min_perf)[0])-1}000")
        if max_perf == 10000:
            y_pmax = 10000
        else:
            y_pmax = int(f"{int(str(max_perf)[0])+1}000")
        y_min = min(y_rmin, y_pmin)
        y_max = max(y_rmax, y_pmax)
        ax.set_yticks([0, 2000, 4000, 6000, 7000, 8000, 9000, 9500, 10000])
        ax.set_xlim(min_date - days_4, max_date + days_4)
        ax.set_ylim(y_min, y_max)
        for i in range(0, 10001, 1000):
            ax.axhspan(i, i+1000, color=rating_colors(i), alpha=0.6, lw=0)
        ax.axhspan(9500, 10000, color=rating_colors(9500), alpha=0.6, lw=0)
        ax.grid(False, "both")
        ax.plot(perf_x, perf_y, marker=".", color="g", label="perf")
        ax.plot(rating_x, rating_y, marker=".", color="r", label="rating")
        ax.legend(bbox_to_anchor=(0, 1), loc='upper left', borderaxespad=0)
        dateFormatter = self.__dateFormatter(ax, max_date, min_date)
        formatter = ticker.FuncFormatter(dateFormatter)
        ax.xaxis.set_major_formatter(formatter)
        fig.savefig(
            f"{get_root_dir()}/data/images/graph.png",
            bbox_inches="tight",
            pad_inches=0.4,
            dpi=300
        )