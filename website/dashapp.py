import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from django_plotly_dash import DjangoDash
from .models import Jd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('JobDashboard', external_stylesheets=external_stylesheets)

# fetch the data
df = pd.DataFrame(Jd.objects.all().values())

# slit skills into list
df['skill'] = df['skill'].str.split(', ')

# Visualization Creation Functions ---------------------------------------------------------------------

# jobs by domain 2019 vs. 2021
df['year'] = pd.DatetimeIndex(df['clean_post_date']).year
df_years = df[(df['year']==2019) | (df['year']==2021)]
df_years = df_years.groupby(['domain_minik', 'year']).count().reset_index().rename(columns={'id':'count',
                                                                                            'domain_minik':'domain'})
df_years['year'] = df_years['year'].astype(int).astype(str)
domain_year_bar = px.bar(df_years,
                         x='domain',
                         y='count',
                         color='year',
                         barmode="group",
                         height=300,
                         title='Job Posts by Domain').update_layout(margin_t=30)

# top 20 in demand skills
def skills_barchart(domain=None):
    if domain is not None:
        skills_df = df[df['domain_minik'] == domain]
    else:
        skills_df = df
    skills_df = skills_df.explode('skill')
    skills_df_count = skills_df[skills_df['skill'].str.strip() != ''].groupby('skill')[
        'id'].count().reset_index().rename(
        columns={'id': 'count'})
    skills_df_count = skills_df_count.sort_values(by='count', ascending=False).iloc[0:20].reset_index().drop(
        columns='index')
    return px.bar(skills_df_count.sort_values(by='count'),
                  x="count",
                  y="skill",
                  title='Top 20 Most Requested Skills',
                  orientation='h',
                  height=500).update_layout(margin_t=30, margin_b=0)

# job posts by state (map)
def jobs_by_state_map(domain=None):
    df['state'] = df['state'].str.replace('US-', '')
    if domain is not None:
        state_count = df[df['domain_minik']==domain]
    else:
        state_count = df
    state_count = state_count.groupby('state').count().reset_index().rename(columns={'id':'count'})
    return px.choropleth(state_count,
                        locations='state',
                        color='count',
                        locationmode='USA-states',
                        color_continuous_scale=['#636EFA', '#EF553B'],
                        scope='usa',
                        title='Job Posts by State',
                        width=600).update_layout(margin_t=30, margin_b=0, margin_r=0, margin_l=0)

# radar chart skills by top companies
def top_company_skills_radar(domain=None):
    if domain is not None:
        top_df = df[df['domain_minik']==domain]
    else:
        top_df = df

    # get top companies - excluding cybercoders, jefferson frank
    top_df['company_name'] = top_df['company_name'].replace('', None).str.strip()
    top_df['company_name'] = np.where(top_df['company_name'].str.contains('amazon', case=False), 'Amazon',
                                      top_df['company_name'])
    top_df['company_name'] = np.where(top_df['company_name'].str.contains('booz allen', case=False), 'Booz Allen Hamilton',
                                      top_df['company_name'])
    top_company_list = list(top_df[top_df['company_name'].notna() & (~top_df['company_name'].isin(['CyberCoders',
                         'Jefferson Frank']))].groupby('company_name').count().reset_index()\
                         .rename(columns={'id':'count'}).sort_values(by='count', ascending=False).reset_index()\
                         .loc[0:4, 'company_name'])

    # get top skills within those companies
    top_company_df = top_df[top_df['company_name'].isin(top_company_list)].explode('skill')
    top_company_df['skill'] = np.where(top_company_df['skill'].str.contains('amazon web service', case=False),
                              'amazon web service', top_company_df['skill'])
    top_company_df = top_company_df[top_company_df['skill']!='']
    top_skill_list = list(top_company_df.groupby('skill').count().reset_index().sort_values(by='id', ascending=False)\
                            .reset_index().loc[0:9, 'skill'])

    # filter to those skills
    top_company_df = top_company_df[top_company_df['skill'].isin(top_skill_list)].groupby(['company_name',
                                      'skill']).count().reset_index().rename(columns={'id':'count'})
    # radar plot
    radar_plot = go.Figure().update_layout(
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.05,
            xanchor='left',
            x=0),
        height=500,
        margin=dict(t=50, r=0, b=0, l=0),
        title='Top 10 Skills Requested by the Top 5 Companies'
    )
    for c in top_company_list:
        curr_company_df = top_company_df[top_company_df['company_name']==c]
        radar_plot.add_trace(go.Scatterpolar(
            r=curr_company_df['count'],
            theta=curr_company_df['skill'],
            name=c
        ))
    return radar_plot

# Dashboard Layout -------------------------------------------------------------------------------------------
app.layout = html.Div(className='row', children=[
    html.Div(className='row', children=[
        html.Div(className='column', children=[
            html.Div(className='row', children=[
                html.Label([
                    'Filter Domain:',
                    dcc.Dropdown(
                        id='domain-selection',
                        options=[{'label': i, 'value': i} for i in df.domain_minik.unique()],
                        value=None
                    )
                ])
            ], style={'padding':'20px'}),
            html.Div(className='row', children=[
                dcc.Graph(
                    id='domain-year-barchart',
                    figure=domain_year_bar
                )
            ], style={'padding':'20px'})
        ], style={'width':'48%'}),
        html.Div(className='column', children=[
            dcc.Graph(
                id='map',
                figure=jobs_by_state_map()
            )
        ], style={'padding':'20px', 'width':'48%'})
    ]),
    html.Div(className='row', children=[
        html.Div(className='column', children=[
            dcc.Graph(
                id='skills-barchart',
                figure=skills_barchart()
            )
        ], style={'padding':'20px', 'width':'48%'}),
        html.Div(className='column', children=[
            dcc.Graph(
                id='skills-radar-plot',
                figure=top_company_skills_radar()
            )
        ], style={'padding':'20px', 'width':'48%'})
    ])
])

# Updates to visualizations when filtering by domains ------------------------------------------------------
@app.callback(
    dash.dependencies.Output('skills-barchart', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value')]
)
def update_skills_barchart(domain):
    return skills_barchart(domain)

@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value')]
)
def update_map(domain):
    return jobs_by_state_map(domain)

@app.callback(
    dash.dependencies.Output('skills-radar-plot', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value')]
)
def update_radar_plot(domain):
    return top_company_skills_radar(domain)
