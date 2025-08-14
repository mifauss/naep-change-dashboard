import numpy as np
import pandas as pd
import streamlit as st
import streamlit_highcharts as hct
import plotly.express as px  # only for colors; optional

# -------------------------
# Helpers
# -------------------------
def state_color_map(states):
    # reuse a nice qualitative palette; repeat if needed
    palette = px.colors.qualitative.Light24
    colors = (palette * ((len(states) // len(palette)) + 1))[: len(states)]
    return {state: colors[i] for i, state in enumerate(states)}

# Highcharts marker symbols we can use:
# 'circle', 'square', 'diamond', 'triangle', 'triangle-down'
PERCENTILE_MARKERS = {10: "circle", 25: "square", 50: "diamond", 75: "triangle", 90: "triangle-down"}

def make_point(row, color, is_selected):
    """Create a Highcharts point dict with per-point marker and custom fields for tooltips."""
    p = int(row["Percentile"])
    symbol = PERCENTILE_MARKERS.get(p, "circle")
    # Larger radius if selected
    radius = 6 if is_selected else 4
    return {
        "x": float(np.rint(row["Score.2019"])),      # baseline score (x)
        "y": float(np.rint(row["Score.Change"])),    # change (y)
        "marker": {"symbol": symbol, "radius": radius, "lineColor": "black", "lineWidth": 1, "fillColor": color},
        "color": color,
        "custom": {
            "state": f"{row['State']}{'*' if bool(row.get('significant', False)) else ''}",
            "percentile": p,
            "score2019": int(np.rint(row["Score.2019"])),
            "score2024": int(np.rint(row["Score.2024"])),
            "change": int(np.rint(row["Score.Change"])),
        },
    }

# -------------------------
# Load data & texts
# -------------------------
data_url = "https://raw.githubusercontent.com/katcast/DataProject/main/Data_for_App_v2.csv"
df = pd.read_csv(data_url)

subjects = sorted(df.Subject.unique())
grades = sorted(df.Grade.unique())
states = sorted(df.State.unique())
state_colors = state_color_map(states)

# About this dashboard text
with open("data/about.txt", "r") as file:
    about_text = file.read()

# How-to text
with open("data/howto.txt", "r") as file:
    howto_text = file.read()

# Title text
with open("data/title.txt", "r") as file:
    title_text = file.read()

ALL_LABEL = "Show All States"
SEL_LABEL = "Select States of Interest from Drop-Down Menu"

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(layout="wide")
st.sidebar.image("data/logo.png", width=200)
st.sidebar.markdown("---")

subject = st.sidebar.radio("Subject", subjects, index=subjects.index("Mathematics"))
grade = st.sidebar.radio("Grade", grades, index=grades.index(8))
display_mode = st.sidebar.radio("Display Mode", [ALL_LABEL, SEL_LABEL], index=0)
selected_states = st.sidebar.multiselect(
    "Selected States",
    states,
    default=[],
    disabled=(display_mode == ALL_LABEL),
    placeholder="Select States",
    label_visibility="collapsed",
)

st.title(title_text)
st.text("")

# Info boxes
# c1, c2 = st.columns([3, 1], gap="large")
# with c1:
st.markdown("#### What This Dashboard Shows")
st.markdown(about_text)
# with c2:
#     st.info(howto_text)

st.text("")

# Filter data
dff = df[(df.Subject == subject) & (df.Grade == grade)]

if display_mode == SEL_LABEL and not selected_states:
    st.warning("Select one or more states to view data.")
else:
    states_to_show = selected_states if display_mode == SEL_LABEL else states

    # Build Highcharts series: one series per state with per-point markers
    series = []
    for state in states_to_show:
        sdf = dff[dff.State == state].sort_values("Percentile")
        significant_any = bool(sdf["significant"].any()) if "significant" in sdf.columns else False
        color = state_colors[state]
        is_selected = state in selected_states

        points = [make_point(row, color, is_selected) for _, row in sdf.iterrows()]

        series.append({
            "type": "line",
            "name": f"{state}{'*' if significant_any else ''}",
            "data": points,
            "color": color,
            "lineWidth": 3 if is_selected else 1,
            "marker": {"enabled": True},     # per-point marker overrides symbol/radius
            "states": {"hover": {"enabled": True}},
            "showInLegend": True,
        })

    # Axis ranges (pad slightly)
    x_min = float(np.floor(dff["Score.2019"].min() - 2))
    x_max = float(np.ceil(dff["Score.2019"].max() + 2))
    y_min = float(np.floor(dff["Score.Change"].min() - 1))
    y_max = float(np.ceil(dff["Score.Change"].max() + 1))

    # Highcharts config
    options = {
        "chart": {"type": "line", "height": 850},
        "title": {"text": f"{subject} Scores for Grade {grade}"},
        "legend": {
            "enabled": True,
            # Default Highcharts legend interactions:
            # single-click toggles visibility; double-click (isolate) can be approximated by ALT+click on many setups.
        },
        "xAxis": {
            "title": {"text": "2019 Score (Baseline)"},
            "min": x_min,
            "max": x_max,
            "gridLineWidth": 1,
            "tickLength": 0,
        },
        "yAxis": {
            "title": {"text": "Change (2024 Score Minus 2019 Score)"},
            "min": y_min,
            "max": y_max,
            "gridLineWidth": 1,
            "plotLines": [  # zero line
                {"value": 0, "width": 2, "color": "black", "zIndex": 5}
            ],
        },
        "tooltip": {
            "useHTML": True,
            # Build tooltip from our custom data fields
            "pointFormat": (
                "<b>{point.custom.state}</b><br/>"
                "Percentile: {point.custom.percentile}th<br/>"
                "2019 Score: {point.custom.score2019}<br/>"
                "2024 Score: {point.custom.score2024}<br/>"
                "Change: {point.custom.change} points"
            ),
            "shared": False,
            'headerFormat': '',
        },
        "plotOptions": {
            "series": {
                "animation": True,
                "stickyTracking": True,
                "states": {"inactive": {"opacity": 0.3}},
            }
        },
        "series": series,
        "credits": {"enabled": False},
        "exporting": {"enabled": True},
    }

    col1, col2, col3 = st.columns([1, 15, 1])
    with col2:
        hct.streamlit_highcharts(options, height="850px", key=f"hc-{subject}-{grade}-{len(states_to_show)}")

    # Optional: small legend for percentile marker shapes
    # (Highcharts doesn't have a built-in multi-shape legend, but you can add a help box or small markdown)
    st.markdown("###### Percentile markers: 10 = ●, 25 = ■, 50 = ◆, 75 = ▲, 90 = ▼")
