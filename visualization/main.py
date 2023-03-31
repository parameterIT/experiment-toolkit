from collections import defaultdict
from datetime import datetime
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.plotting import show
import os
import pandas as pd
import bokeh
from typing import List, Tuple


def main():
    figures = get_figure()
    gridplots = gridplot(
        [[figures[i], figures[i + 1]] for i in range(0, len(figures) - 1, 2)],
    )
    show(gridplots)


def read_data(tool: str):
    path = "./output/" + tool + "/frequencies/"
    graph_data = defaultdict(list)
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        tagNumber = get_tag_number(tool, filename)
        df = pd.read_csv(filepath, skiprows=0)
        for metric, value in df.itertuples(index=False, name=None):
            graph_data[metric].append((tagNumber, value))
    for _, v in graph_data.items():
        v.sort()
    return graph_data


def get_tag_number(tool: str, filename):
    path = "./output/" + tool + "/metadata/"
    filepath = os.path.join(path, filename)
    df = pd.read_csv(filepath, skiprows=0)
    for qm, src in df.itertuples(index=False, name=None):
        path_parts = src.split("/")
        return path_parts[len(path_parts) - 1]


# def _get_line(data, key):
#     x = [(value[0]) for value in data[key]]
#     y = [(value[1]) for value in data[key]]
#     p = figure(
#         width=600,
#         height=350,
#         title=key,
#         x_axis_label="Tag Nr.",
#         y_axis_label="No. Violations",
#     )
#     p.line(x, y, legend_label="Progress", line_width=2)
# return p


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
        legend_label="byoqm",
        line_width=2,
        color="red",
    )
    p.xaxis.major_label_orientation = "vertical"
    return p


def get_figure():
    code_climate_data = read_data("code_climate")
    byoqm_data = read_data("byoqm")
    figures = []
    for metric, code_climate_values in code_climate_data.items():
        byoqm_values = byoqm_data[metric]
        if metric == "method_complexity":
            byoqm_values = byoqm_data["cognitive_complexity"]
        figures.append(_get_line(code_climate_values, byoqm_values, metric))

    return figures


if __name__ == "__main__":
    main()
