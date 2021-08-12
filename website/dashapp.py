import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from django_plotly_dash import DjangoDash
from .models import Jd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('JobDashboard', external_stylesheets=external_stylesheets)

# fetch the data
df = pd.DataFrame(Jd.objects.all().values())

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
df['skill'] = df['skill'].str.split(', ')
skills_df = df.explode('skill')
skill_count = skills_df[skills_df['skill'].str.strip()!=''].groupby('skill')['id'].count().reset_index().rename(columns={'id':'count'})
skill_count = skill_count.sort_values(by='count', ascending=False).iloc[0:20].reset_index().drop(columns='index')
top_skills_bar = px.bar(skill_count.sort_values(by='count'),
                        x="count",
                        y="skill",
                        title='Top 20 Most Requested Skills',
                        orientation='h',
                        height=500).update_layout(margin_t=30)

# postings by state
# clean up the weird MI state:
df['state'] = df['state'].str.replace('US-', '')
state_count = df.groupby('state').count().reset_index().rename(columns={'id':'count'})
map_fig = px.choropleth(state_count,
                    locations='state',
                    color='count',
                    hover_name='count',
                    locationmode='USA-states',
                    color_continuous_scale=['#636EFA', '#EF553B'],
                    scope='usa',
                    title='Job Posts by State').update_layout(margin_t=30)

app.layout = html.Div(
    className='row',
    children=[
        html.Div(
            className='column',
            children=[
                html.Div(
                    className='row',
                    children=[
                        html.Label([
                            'Filter Domain:',
                            dcc.Dropdown(
                                id='domain-selection',
                                options=[{'label': i, 'value': i} for i in df.domain_minik.unique()],
                                value=None
                            )
                        ])
                    ],
                    style={'padding':'20px'}
                ),
                html.Div(
                    className='row',
                    children=[
                        dcc.Graph(
                            id='skills-barchart',
                            figure=top_skills_bar
                        )
                    ],
                    style={'padding':'20px'}
                )
            ],
            style={'display':'inline-block', 'width':'48%'}
        ),
        html.Div(
            className='column',
            children=[
                html.Div(
                    className='row',
                    children=[
                        dcc.Graph(
                            id='domain-year-barchart',
                            figure=domain_year_bar
                        )
                    ],
                    style={'padding':'20px'}
                ),
                html.Div(
                    className='row',
                    children=[
                        dcc.Graph(
                            id='map',
                            figure=map_fig
                        )
                    ],
                    style={'padding':'20px'}
                )
            ],
            style={'display':'inline-block', 'width':'48%'}
        )
    ],
    style={'margin':'20px'}
)

@app.callback(
    dash.dependencies.Output('skills-barchart', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value')]
)
def update_skills_barchart(domain):
    if domain is not None:
        filtered_df = skills_df[skills_df['domain_minik']==domain]
        filtered_skill_count = filtered_df[filtered_df['skill'].str.strip() != ''].groupby('skill')['id'].count().reset_index().rename(
            columns={'id': 'count'})
        filtered_skill_count = filtered_skill_count.sort_values(by='count', ascending=False).iloc[0:20].reset_index().drop(columns='index')
        return px.bar(filtered_skill_count.sort_values(by='count'),
                      x="count",
                      y="skill",
                      title='Top 20 Most Requested Skills',
                      orientation='h',
                      height=500).update_layout(margin_t=30)
    else:
        return top_skills_bar

@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value')]
)
def update_skills_barchart(domain):
    if domain is not None:
        filtered_state_count = df[df['domain_minik'] == domain]
        filtered_state_count = filtered_state_count.groupby('state').count().reset_index().rename(columns={'id': 'count'})
        return px.choropleth(filtered_state_count,
                                locations='state',
                                color='count',
                                hover_name='count',
                                locationmode='USA-states',
                                color_continuous_scale=['#636EFA', '#EF553B'],
                                scope='usa',
                                title='Job Posts by State').update_layout(margin_t=30)
    else:
        return map_fig

