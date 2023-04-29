from collections import defaultdict
from datetime import datetime
import logging
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.io import export_png
import os
import pandas as pd
from typing import List, Tuple
import sys

all_metrics = [
    "method_lines", "file_lines", "argument_count", "complex_logic", "method_count", "return_statements", "identical-code", "similar-code", "nested_control_flow", "cognitive-complexity", "duplication"
    ]

def main():
    file_prefix = ""
    if len(sys.argv) > 1:
        # The second argument passed to the program is a common file prefix for output
        # png files for better organisation, not passing the argument adds no prefix
        file_prefix = sys.argv[1]
        try:
            file_prefix_length = int(sys.argv[2])
        except ValueError:
            print("Wrong type input.. poetry run main [STRING] [INT] ")
            exit()

    figures = get_figure(file_prefix_length)
    for f in figures:
        export_png(f, filename=f"imgs/{file_prefix}-{f.title.text}.png")

def read_data(tool: str, prefixlength : int):
    path = "./output/" + tool + "/outcomes/"
    graph_data = defaultdict(list)
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        tag_number = get_tag_number(tool, filename)
        df = pd.read_csv(
            filepath,
            skiprows=0,
            dtype={"value": int, "metric": str},
            # Assumes that maintainabilty (the only non-int value) is at the bottom of
            # each csv file
            skipfooter=1,
            engine="python",
        )

        for metric, value in df.itertuples(index=False, name=None):
            graph_data[metric.lower()].append((tag_number, value))
            print("Adding", value, "for", metric, "for tag", tag_number)

        for metric in all_metrics:
            if len(graph_data[metric]) == 0 or graph_data[metric][len(graph_data[metric])-1][0] != tag_number:
                graph_data[metric].append((tag_number, 0))
                print("Adding 0 for", metric, "for tag", tag_number)


    for _, v in graph_data.items():
        v.sort(key=lambda t: gen_key(t[0][int(prefixlength):]))

    return graph_data

def gen_key(string):
    sum = 0
    counter = 1000000000
    for v in string.split("."):
        try:
            sum += int(v) * (10 * counter)
        except:
            sp = 0
            for l in v:
                try:
                    int(l)
                    sp += 1
                except:
                    break
            sum += int(v[0:sp]) * (10 * counter)
        counter = counter / 100
    for l in string[2:]:
        if l.lower() == "-":
            continue
        if l.lower() == "r":
            sum -= 60
            continue
        if l.lower() == "c":
            sum -= 60
            continue
        if l.lower() == "m":
            sum -= 200
            continue
        sum += ord(l)
    return sum

def get_tag_number(tool: str, filename):
    path = "./output/" + tool + "/metadata/"
    filepath = os.path.join(path, filename)
    df = pd.read_csv(filepath, skiprows=0)
    for qm, src in df.itertuples(index=False, name=None):
        path_parts = src.split("/")
        return path_parts[len(path_parts) - 1]


def _get_line(
    one_qm_data: List[Tuple[int, str]],
    other_qm_data: List[Tuple[int, str]],
    metric: str,
):
    one_qm_xs = [data_point[0] for data_point in one_qm_data]
    one_qm_ys = [data_point[1] for data_point in one_qm_data]
    other_qm_xs = [data_point[0] for data_point in other_qm_data]
    other_qm_ys = [data_point[1] for data_point in other_qm_data]

    p = figure(
        width=600,
        height=350,
        title=metric,
        x_range=one_qm_xs,
        x_axis_label="Tag",
        y_axis_label="No. Violations",
    )
    p.line(one_qm_xs, one_qm_ys, legend_label="code_climate", line_width=2)
    p.line(
        other_qm_xs,
        other_qm_ys,
        legend_label="modu",
        line_width=2,
        color="red",
    )
    p.xaxis.major_label_orientation = "vertical"
    max_element = max(one_qm_ys + other_qm_ys)
    try:
        if max_element != 0:
            p.y_range = Range1d(0, int(max_element) * 1.1)
    except ValueError:
        logging.warning(("No data to plot created for", metric))
        return
    return p


def get_figure(prefixlength : int) -> List[figure]:
    code_climate_data = read_data("code_climate", prefixlength)
    modu_data = read_data("modu", prefixlength)
    figures = []
    for metric, code_climate_values in code_climate_data.items():
        # coupled with the the modu tool, since all metrics of the of modu's
        # implementation of code climate are lower-case
        modu_values = modu_data[metric.lower()]
        # if-elif chain coupled with the modu tool to translate metrics reported by
        # code climate's API with the names of the metrics in modu's implementation of
        # code climate
        if metric == "method_complexity":
            modu_values = modu_data["cognitive_complexity"]
        elif metric == "identical-code":
            modu_values = modu_data["identical_code"]
        elif metric == "similar-code":
            modu_values = modu_data["similar_code"]
        figures.append(_get_line(code_climate_values, modu_values, metric))

    return figures


if __name__ == "__main__":
    main()
