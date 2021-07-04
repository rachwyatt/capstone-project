# Run this app with `python dashboard.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# toy data set exploring domain by state
df = pd.DataFrame({
    "Domain": ["Healthcare", "Sports", "Public Service", "Business", "Consulting", "Healthcare", "Sports", "Public Service", "Business", "Consulting"],
    "Count": [90, 76, 34, 105, 67, 42, 93, 121, 45, 44],
    "State": ["California", "New York", "California", "New York", "California", "New York", "California", "New York", "California", "New York"]
})

# bar graph example (could be a map...)
fig = px.bar(df, x="Domain", y="Count", color="State", barmode="group", title="Example Using Toy Data Set (This could be a map...?)")

app.layout = html.Div(children=[
    html.H1(children='Data Science Job Exploration'),

    html.Div(children='''
        Capstone Project - This is a dummy dashboard...just trying to setup the structure a bit.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)