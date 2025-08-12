import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


def get_tooltip_data(row: pd.Series) -> pd.DataFrame:
    """Data frame attached to each marker and used to display tooltip."""
    data = [
        f"{row['State']}{'*' if row['significant'] else ''}",
        row["Percentile"],
        [np.rint(row["Score.2019"])],
        [np.rint(row["Score.2024"])],
        [np.rint(row["Score.Change"])],
    ]
    index = range(len(data))
    return pd.DataFrame(dict(zip(index, data)))


# Load data from GitHub
data_url = "https://raw.githubusercontent.com/katcast/DataProject/main/Data_for_App_v2.csv"
df = pd.read_csv(data_url)

# Extract unique options
subjects = sorted(df.Subject.unique())
grades = sorted(df.Grade.unique())
states = sorted(df.State.unique())

# Assign colors to states
color_palette = px.colors.qualitative.Light24
state_colors = {state: color_palette[i % len(color_palette)] for i, state in enumerate(states)}

# Define markers for percentiles
percentile_markers = {10: "circle", 25: "square", 50: "diamond", 75: "x", 90: "star"}

# Template for mouse-over popover
hovertemplate = (
    "<b>%{customdata[0]}</b><br>"
    "Percentile: %{customdata[1]}th<br>"
    "2019 Score: %{customdata[2]:.0f}<br>"
    "2024 Score: %{customdata[3]:.0f}<br>"
    "Change: %{customdata[4]:.0f} points<br>"
    "<extra></extra>"
)

# About this dashboard text
with open("data/about.txt", "r") as file:
    about_text = file.read()

# How-to text
with open("data/howto.txt", "r") as file:
    howto_text = file.read()

# Title text
with open("data/title.txt", "r") as file:
    title = file.read()

# Show all/selected labels
all_label = "Show All States"
selected_label = "Select States of Interest from Drop-Down Menu"

# Use whole page width
st.set_page_config(layout="wide")

# Sidebar inputs
st.sidebar.image("data/logo.png", width=200)
st.sidebar.markdown("---")
subject = st.sidebar.radio("Subject", subjects, index=subjects.index("Mathematics"))
grade = st.sidebar.radio("Grade", grades, index=grades.index(8))
display_mode = st.sidebar.radio("Display Mode", [all_label, selected_label], index=0)
selected_states = st.sidebar.multiselect(
    "Selected States",
    states,
    default=[],
    disabled=(display_mode == all_label),
    placeholder="Select States",
    label_visibility="collapsed",
)

# Title, subtitle and legend help
st.title("State Change by Baseline Scores Dashboard: Using NAEP Data")
st.text("")

# Flex-container for about and text
outer_container = st.container(horizontal=True, gap="large", vertical_alignment="top")
about_container = outer_container.container(border=False)
about_container.markdown("#### What This Dashboard Shows")
about_container.markdown(about_text)
help_container = outer_container.container(border=False, width=240, height=250)
help_container.info(howto_text, icon=":material/help:", width="stretch")

# Spacer
st.text("")

# Filter data by subject and grade
dff = df[(df.Subject == subject) & (df.Grade == grade)]

# Initialize figure
fig = go.Figure()

if display_mode == selected_label and not selected_states:
    st.warning("Select one or more states to view data.")
else:
    # States to show
    states_to_show = selected_states if display_mode == selected_label else states

    # Iterate over states to show
    for n, state in enumerate(states_to_show):

        # Get data for current state and order by percentiles
        sdf = dff[dff.State == state].sort_values("Percentile")

        # Add markers with custom shapes for each percentile
        for _, row in sdf.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[row["Score.2019"]],
                    y=[row["Score.Change"]],
                    mode="markers",
                    customdata=get_tooltip_data(row),
                    hovertemplate=hovertemplate,
                    showlegend=False,
                    legendgroup=state,
                    marker=dict(
                        symbol=percentile_markers.get(row["Percentile"], "circle"),
                        color=state_colors[state],
                        size=14,
                    ),
                )
            )

        # Draw lines connecting markers
        fig.add_trace(
            go.Scatter(
                x=sdf["Score.2019"],
                y=sdf["Score.Change"],
                mode="lines",
                name=f"{state}{'*' if sdf['significant'].any() else ''}",
                showlegend=True,
                legendgroup=state,
                hoverinfo="skip",
                line=dict(
                    color=state_colors[state],
                    width=3,
                ),
            )
        )

    # Customize figure
    fig.update_layout(
        xaxis=dict(
            range=(dff["Score.2019"].min() - 2, dff["Score.2019"].max() + 2),
            tickfont=dict(size=16),
            showgrid=True,
        ),
        yaxis=dict(
            range=(dff["Score.Change"].min() - 0.2, dff["Score.Change"].max() + 0.2),
            tickfont=dict(size=16),
            showgrid=True,
        ),
        xaxis_title=dict(text="2019 Score", font=dict(size=18)),
        yaxis_title=dict(text="Change (2024 - 2019)", font=dict(size=18)),
        margin=dict(t=60),
        title=dict(text=f"{subject} Scores for Grade {grade}", font=dict(size=28)),
        legend=dict(font=dict(size=16)),
        template="plotly_white",
        height=750,
        hoverlabel=dict(font_size=16),
    )

    # Highlight x-axis/zeroline
    fig.update_yaxes(zeroline=True, zerolinecolor="black", zerolinewidth=2)

    # Show figure
    st.plotly_chart(fig, use_container_width=True, on_select="ignore")

    # Add legend (Legend entries are just images. This is not great, but it works for now.)
    cols = st.columns(6, gap="small")
    for col, percentile in zip(cols[:-1], [10, 25, 50, 75, 90]):
        col.image(f"data/P{percentile}.png", width=178)
