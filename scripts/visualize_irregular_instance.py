import argparse
import json
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots
import numpy as np
import math

def shape_path(path_x, path_y, shape, is_hole=False):
    # How to draw a filled circle segment?
    # https://community.plotly.com/t/how-to-draw-a-filled-circle-segment/59583
    # https://stackoverflow.com/questions/70965145/can-plotly-for-python-plot-a-polygon-with-one-or-multiple-holes-in-it
    for element in (shape if not is_hole else reversed(shape)):
        t = element["type"]
        xs = element["start"]["x"]
        ys = element["start"]["y"]
        xe = element["end"]["x"]
        ye = element["end"]["y"]
        if t == "CircularArc":
            xc = element["center"]["x"]
            yc = element["center"]["y"]
            anticlockwise = 1 if element["anticlockwise"] else 0
            rc = math.sqrt((xc - xs)**2 + (yc - ys)**2)

        if is_hole:
            xs, ys, xe, ye = xe, ye, xs, ys

        if len(path_x) == 0 or path_x[-1] is None:
            path_x.append(xs)
            path_y.append(ys)

        if t == "LineSegment":
            path_x.append(xe)
            path_y.append(ye)
        elif t == "CircularArc":
            start_cos = (xs - xc) / rc
            start_sin = (ys - yc) / rc
            start_angle = math.atan2(start_sin, start_cos)
            end_cos = (xe - xc) / rc
            end_sin = (ye - yc) / rc
            end_angle = math.atan2(end_sin, end_cos)
            if anticlockwise and end_angle <= start_angle:
                end_angle += 2 * math.pi
            if not anticlockwise and end_angle >= start_angle:
                end_angle -= 2 * math.pi

            t = np.linspace(start_angle, end_angle, 1024)
            x = xc + rc * np.cos(t)
            y = yc + rc * np.sin(t)
            for xa, ya in zip(x[1:], y[1:]):
                path_x.append(xa)
                path_y.append(ya)
    path_x.append(None)
    path_y.append(None)


parser = argparse.ArgumentParser(description='')
parser.add_argument('csvpath', help='path to JSON file')
args = parser.parse_args()

bin_types_x = []
bin_types_y = []
defects_x = []
defects_y = []
item_types_x = []
item_types_y = []

with open(args.csvpath, 'r') as f:
    j = json.load(f)

    for bin_type_id, bin_type in enumerate(j["bin_types"]):
        bin_types_x.append([])
        bin_types_y.append([])
        defects_x.append([])
        defects_y.append([])

        shape_path(
                bin_types_x[bin_type_id],
                bin_types_y[bin_type_id],
                bin_type["elements"])
        for defect in (bin_type["defects"]
                       if "defects" in bin_type else []):
            shape_path(
                    defects_x[bin_type_id],
                    defects_y[bin_type_id],
                    defect["elements"])
            for hole in (defect["holes"]
                         if "holes" in defect else []):
                shape_path(
                        defects_x[bin_type_id],
                        defects_y[bin_type_id],
                        hole["elements"],
                        True)

    for item_type_id, item_type in enumerate(j["item_types"]):
        item_types_x.append([])
        item_types_y.append([])
        for item_shape in item_type["shapes"]:
            shape_path(
                    item_types_x[item_type_id],
                    item_types_y[item_type_id],
                    item_shape["elements"])
            for hole in (item_shape["holes"]
                         if "holes" in item_shape else []):
                shape_path(
                        item_types_x[item_type_id],
                        item_types_y[item_type_id],
                        hole["elements"],
                        True)

m = len(bin_types_x)
n = len(item_types_x)
colors = px.colors.qualitative.Plotly
fig = plotly.subplots.make_subplots(
        rows=m + n,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.001)

for i in range(0, m):

    fig.add_trace(go.Scatter(
        x=bin_types_x[i],
        y=bin_types_y[i],
        name="Bin types",
        legendgroup="bin types",
        showlegend=(i == 0),
        marker=dict(
            color='black',
            size=1)),
        row=i + 1,
        col=1)

    fig.add_trace(go.Scatter(
        x=defects_x[i],
        y=defects_y[i],
        name="Defects",
        legendgroup="defects",
        showlegend=(i == 0),
        fillcolor="crimson",
        fill="toself",
        marker=dict(
            color='black',
            size=1)),
        row=i + 1,
        col=1)

for i in range(0, n):

    fig.add_trace(go.Scatter(
        x=item_types_x[i],
        y=item_types_y[i],
        name="Item types",
        legendgroup="item types",
        showlegend=(i == 0),
        fillcolor="cornflowerblue",
        fill="toself",
        marker=dict(
            color='black',
            size=1)),
        row=m + i + 1,
        col=1)

# Plot.
fig.update_layout(
        autosize=True,
        height=(m + n)*1000)
fig.update_xaxes(
        rangeslider=dict(visible=False))
fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1)
fig.show()
