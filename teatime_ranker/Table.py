import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from .util import get_root_dir, datetime_today, str_today, rating_colors, pretty_float


class Table:
    def __init__(self, result):
        self.result = result
        fe = fm.FontEntry(
            fname=f"{get_root_dir()}/data/fonts/mgenplus-1cp-regular.ttf",
            name="Mgen+ 1cp Regular"
        )
        fm.fontManager.ttflist = [fe]
        mpl.rcParams["font.family"] = "Mgen+ 1cp Regular"
        mpl.rcParams["font.size"] = 30
        
    def calc_date(self, ms):
        date = datetime_today()
        date = date.replace(hour=15)
        date += datetime.timedelta(milliseconds=ms)
        return date.strftime("%H:%M:%S.%f")[:-3]
    
    def make_table(self):
        cell_text = []
        cell_colours = []
        column_labels = ["No", "name", "record", "perf", "rating", "diff"]
        column_widths = [0.1, 0.4, 0.4, 0.2, 0.2, 0.15]
        for r in self.result:
            cell_text.append([
                r["no"],
                r["screen_name"],
                self.calc_date(r["ms"]),
                pretty_float(f"{r['perf']:.2f}"),
                pretty_float(f"{r['rating']:.2f}"),
                pretty_float(f"{r['diff']:.2f}")
            ])
            cell_colours.append(["#FFFFFF"] + [rating_colors(r["perf"])]*5)
        fig, ax = plt.subplots()
        ax.axis("off")
        table = ax.table(
            cellText=cell_text,
            cellColours=cell_colours,
            colLabels=column_labels,
            colWidths=column_widths,
            loc="center",
            cellLoc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)
        fig.savefig(
            f"{get_root_dir()}/data/images/{str_today()}.png",
            bbox_inches="tight",
            pad_inches=0,
            facecolor="azure",
            dpi=300
        )