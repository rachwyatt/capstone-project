import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
import pymysql
from django_plotly_dash import DjangoDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('JobDashboard')

# fetch the data
# connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com",
#                              user="root",
#                              password="mads_capstone",
#                              database="capstone",
#                              port=3306,
#                              charset='utf8mb4',
#                              cursorclass=pymysql.cursors.DictCursor)
#
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM jd LIMIT 100;")
# table = cursor.fetchall()
# connection.close()
#
# df = pd.json_normalize(table)

# toy data set exploring domain by state
df = pd.DataFrame({
    "Domain": ["Healthcare", "Healthcare", "Healthcare", "Healthcare",
               "Sports", "Sports", "Sports", "Sports",
               "Public Service", "Public Service", "Public Service", "Public Service",
               "Business", "Business", "Business", "Business"],
    "Count": np.random.uniform(low=10, high=300, size=(16,)).round(),
    "Region": ["West", "Midwest", "South", "North East",
               "West", "Midwest", "South", "North East",
               "West", "Midwest", "South", "North East",
               "West", "Midwest", "South", "North East"]
})

# bar graph example (could be a map...)
fig = px.bar(df, x="Domain", y="Count", color="Region", barmode="group", title="Domain by Region (Toy Data Set)")

app.layout = html.Div(children=[
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])
