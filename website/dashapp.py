import dash
import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
import pymysql
from django_plotly_dash import DjangoDash
from .models import Jd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('JobDashboard')

# fetch the data
df = pd.DataFrame(Jd.objects.all().values())

# top 100 in demand skills
df['skill'] = df['skill'].str.split(', ')
df = df.explode('skill')
skill_count = df[df['skill'].str.strip()!=''].groupby('skill')['id'].count().reset_index().rename(columns={'id':'count'})
skill_count = skill_count.sort_values(by='count', ascending=False).iloc[0:50].reset_index().drop(columns='index')
fig = px.bar(skill_count.sort_values(by='count'), x="count", y="skill", title="Most Requested Skills", orientation='h')

app.layout = html.Div(children=[
    dcc.Graph(
        id='skills',
        figure=fig
    )
])
