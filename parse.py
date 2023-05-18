#!/bin/python3

import glob
import csv
from typing import List, Dict
from dataclasses import dataclass
from argparse import ArgumentParser
from datetime import date, datetime
import matplotlib.pyplot as plt


### models ###

@dataclass
class StockItem:
    name: str
    isin: str
    rate_ct: int
    pieces_100: int
    def total_ct(self):
        return self.rate_ct * self.pieces_100 / 100

@dataclass
class Report:
    date: date
    items: List[StockItem]
    def __str__(self):
        # tiny bit of formatting
        ret = "Report(date=" + self.date.isoformat() + ", items=[\n"
        for p in self.items:
            ret += "\t" + str(p) + ",\n"
        ret += "])"
        return ret


### helper functions ###

def parseReport(f) -> Report:
    cr = csv.reader(f, delimiter=";", quotechar="\"")
    row_list = [x for x in cr]
    # line 4 (3 if counted from 0)
    date = datetime.strptime(row_list[3][1], "%d.%m.%Y %H:%M")
    # actual listing starts at 7 (6 if from 0)
    items = []
    for i in range(6, len(row_list)):
        r = row_list[i]
        items.append(StockItem(r[3], r[2], int(r[4].replace(",", "")),
                                       int(r[0].replace(",", ""))))
    return Report(date, items)

def create_time_series(p_fun) -> Dict:
    # build a time series to make pyplot happy
    named_data_series = {}
    for r in list_of_reports:
        for p in r.items:
            if p.name in named_data_series:
                named_data_series[p.name].append((r.date, p_fun(p)))
            else:
                named_data_series[p.name] = [(r.date, p_fun(p))]
    return named_data_series

### main code ###

arg_parser = ArgumentParser(
    description="Small parser/visualization tool for the DKB stock/portfolio CSV export")
arg_parser.add_argument("-f", help="path to the folder with the csv [f]iles",
                         required=True)
arg_parser.add_argument("-t", action='store_true', help="draw [t]otal values")
arg_parser.add_argument("-n", action='store_true', help="draw [n]umber of shares/...")
arg_parser.add_argument("-r", action='store_true', help="draw [r]ate of items")
arg_parser.add_argument("-d", action='store_true', help="[d]ump parsed data (for debugging)")
args = arg_parser.parse_args()
# find files, read and parse
csv_file_names = glob.glob(glob.escape(args.f) + "/*.csv")
list_of_reports = []
for fn in csv_file_names:
    with open(fn, "r", encoding="ISO-8859-1") as f:
        list_of_reports.append(parseReport(f))
# enforce some sorting
list_of_reports.sort(key=lambda r: r.date)
for r in list_of_reports:
    r.items.sort(key=lambda r: r.isin)

if args.d:
    for report in list_of_reports:
        print(report)
list_of_time_series = []
names_of_plots = []
if args.t:
    list_of_time_series.append(create_time_series(lambda p: p.total_ct()/100))
    names_of_plots.append("Total Values")
if args.n:
    list_of_time_series.append(create_time_series(lambda p: p.pieces_100/100))
    names_of_plots.append("Numbers of Shares/...")
if args.r:
    list_of_time_series.append(create_time_series(lambda p: p.rate_ct/100))
    names_of_plots.append("Rates per Item")

# actual drawing
lstyles = ["solid", "dashed", "dashdot", "dotted"]
fig, axs = plt.subplots(len(list_of_time_series), 1, sharex=True)
for i in range(0, len(list_of_time_series)):
    ts = list_of_time_series[i]
    for n in ts:
        axs[i].step([x[0] for x in ts[n]],
                  [x[1] for x in ts[n]],
                    label=n, marker="x", ls=lstyles[i])
        axs[i].set_title(names_of_plots[i])
        axs[i].grid(True)
        axs[i].legend()

plt.show()
