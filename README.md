State Change NAEP Scores Dashboard
=======================

Visualize the relationship between pre-COVID scores (2019) and score changes since the pandemic (2024–2019) across different percentiles for states and jurisdictions in NAEP assessments.

## Run

Make sure all dependencies are installed and then run
```
streamlit run dashboard.py
```
in the project folder.

## Description

This dashboard visualizes the relationship between pre-COVID scores (2019) and score changes since the pandemic (2024–2019) across different percentiles for states and jurisdictions in NAEP assessments.
 
Each line represents a state, connecting the score change at several percentile points (10th, 25th, 50th, 75th, and 90th). These lines illustrate how changes varied across the achievement distribution within each state. A horizontal line at zero helps distinguish states or percentile points within states with positive changes (above) from those with negative changes (below).
 
If the difference between a state’s 10th and 90th percentile points is statistically significant (p < 0.05), this is indicated with an asterisk next to the state’s name in the legend.

## Getting Started

Use the menu on the left to choose the subject, grade, and whether you'd like to compare all states or only selected ones.
 
You can interact with the plot one of two ways:
 
Using the **legend**: 
* **Single-click** a state in the legend to toggle its line on or off. 
* **Double-click** a legend entry to isolate that state’s line; double-click again to restore all the lines.
 
Using the **selection menu**:
* Select states from the drop-down menu to view their lines only. Click the “x” next to a state name to de-select it.
 
Note that selecting states in the menu on the left is different from clicking their entries in the legend. Think of the selection menu as defining the *data*, and the legend clicks as toggling *visibility*.