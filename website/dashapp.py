import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from .models import Jd

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = DjangoDash('JobDashboard', external_stylesheets=external_stylesheets)

# fetch the data
df = pd.DataFrame(Jd.objects.all().values())

# slit skills into list
df['skill'] = df['skill'].str.title()\
    .str.replace('Aws', 'AWS')\
    .str.replace('Sql', 'SQL')\
    .str.replace('Sas', 'SaS')\
    .str.replace('Nlp', 'NLP')\
    .str.split(', ')
df = df.rename(columns={'skill':'Skill'})

# clean up states a little
df['state'] = df['state'].str.replace('US-', '')
df['state'] = df['state'].astype(str)

# get list of states for state filter
state_names = pd.read_csv('state_abbrev.csv')
state_names['name'] = state_names['name'].str.title()
state_list = sorted([i for i in df['state'].unique() if (len(i) < 3) & (i not in ['', 'NN', 'UK', 'QC', 'NS',
                                                                                  'ON', 'BC', 'W', 'VI', 'PR'])])
states = state_names[state_names['abbrev'].isin(state_list)]

# Capitalize domains -------------------------------------------------------------------------------
df['domain_lr'] = df['domain_lr'].str.title().str.replace('And ', 'and ')
df['domain_minik'] = df['domain_minik'].str.title().str.replace('And ', 'and ')

# Generate domain list for dropdown menu --------------------------------------------------------------
def domain_list(model='domain_lr'):
    return [{'label': i, 'value': i} for i in sorted(df[model].unique())]

# Visualization Creation Functions ---------------------------------------------------------------------

# jobs by domain
def jobs_by_domain_barchart(model='domain_lr', state=None):
    if state is not None:
        df_domains = df[df['state'] == state]
    else:
        df_domains = df
    df_domains = df_domains.groupby([model]).count().reset_index().rename(columns={'id':'Count', model:'Domain'}).\
        sort_values(by='Count', ascending=False)
    return px.bar(df_domains,
        x='Domain',
        y='Count',
        height=300).update_layout(margin_t=30).update_traces(marker_color='#636EFA')

# top 20 in demand skills
def skills_barchart(domain=None, model='domain_lr', state=None):
    if domain is not None:
        skills_df = df[df[model] == domain]
    else:
        skills_df = df
    if state is not None:
        skills_df = skills_df[skills_df['state'] == state]
    skills_df = skills_df.explode('Skill')
    skills_df_count = skills_df[skills_df['Skill'].str.strip() != ''].groupby('Skill')[
        'id'].count().reset_index().rename(
        columns={'id': 'Count'})
    skills_df_count = skills_df_count.sort_values(by='Count', ascending=False).iloc[0:20].reset_index().drop(
        columns='index')
    return px.bar(skills_df_count.sort_values(by='Count'),
                  x="Count",
                  y="Skill",
                  orientation='h',
                  height=500).update_layout(margin_t=30, margin_b=0).update_traces(marker_color='#00CC96')

# job posts by state (map)
def jobs_by_state_map(domain=None, model='domain_lr'):
    if domain is not None:
        state_count = df[df[model]==domain]
    else:
        state_count = df
    state_count = state_count.groupby('state').count().reset_index().rename(columns={'id':'Count'})
    return px.choropleth(state_count,
                        locations='state',
                        color='Count',
                        locationmode='USA-states',
                        color_continuous_scale=['#636EFA', '#00CC96', '#FECB52', '#FFA15A', '#EF553B'],
                        scope='usa',
                        height=300).update_layout(margin_t=30, margin_b=0, margin_r=0, margin_l=0)

# radar chart skills by top companies
def top_company_skills_radar(domain=None, model='domain_lr', state=None):
    if domain is not None:
        top_df = df[df[model]==domain]
    else:
        top_df = df
    if state is not None:
        top_df = top_df[top_df['state'] == state]

    # get top companies
    top_df['company_name'] = top_df['company_name'].replace('', None).str.strip()
    top_df['company_name'] = np.where(top_df['company_name'].str.contains('amazon', case=False), 'Amazon',
                                      top_df['company_name'])
    top_df['company_name'] = np.where(top_df['company_name'].str.contains('booz allen', case=False), 'Booz Allen Hamilton',
                                      top_df['company_name'])
    top_company_list = list(top_df[top_df['company_name'].notna()].groupby('company_name').count().reset_index()
                         .rename(columns={'id':'Count'}).sort_values(by='Count', ascending=False).reset_index()
                         .loc[0:4, 'company_name'])

    # get top skills within those companies
    top_company_df = top_df[top_df['company_name'].isin(top_company_list)].explode('Skill')
    top_company_df['Skill'] = np.where(top_company_df['Skill'].str.contains('amazon web service', case=False),
                              'amazon web service', top_company_df['Skill'])
    top_company_df = top_company_df[top_company_df['Skill']!='']
    top_skill_list = list(top_company_df.groupby('Skill').count().reset_index().sort_values(by='id', ascending=False)
                          .reset_index().loc[0:9, 'Skill'])

    # filter to those skills
    top_company_df = top_company_df[top_company_df['Skill'].isin(top_skill_list)].groupby(['company_name',
                                      'Skill']).count().reset_index().rename(columns={'id':'Count'})
    # radar plot
    radar_plot = go.Figure().update_layout(
        margin=dict(t=20, r=20, b=50, l=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="left",
            x=0.01
        ),
        height=450
    )
    for c in top_company_list:
        curr_company_df = top_company_df[top_company_df['company_name']==c]
        radar_plot.add_trace(go.Scatterpolar(
            r=curr_company_df['Count'],
            theta=curr_company_df['Skill'],
            name=c
        ))
    return radar_plot

# Dashboard Layout -------------------------------------------------------------------------------------------
app.layout = html.Div([
    dbc.Container([
        dbc.Alert('This dashboard does not reflect current job postings but offers a broad look at jobs that were posted 2019-2021.'
                  ' The job posts featured here are all data science related and were assigned domains (industries or sectors)'
                  ' by using two different models: logistic regression and mini-batch k-means. Please explore the dashboard'
                  ' to gather insights about the companies, states, and domains with the most data science job opportunities'
                  ' as well as the most in demand skills in various domains and regions.',
                  color='warning', dismissable=True),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Label([
                        'Filter Domain:',
                        dcc.Dropdown(
                            id='domain-selection',
                            options=domain_list(),
                            value=None
                        )
                    ], style={'width':'100%'}, id='domain-tooltip'),
                    dbc.Tooltip(
                        'Filters all charts except "Job Posts by Domain"',
                        target='domain-tooltip'
                    )
                ], style={'padding-left':'20px', 'padding-right':'20px', 'margin-bottom':'0px'}),
                dbc.Row([
                    dcc.RadioItems(
                        id='model-selection',
                        options=[
                            {'label': 'Logistic Regression Model', 'value': 'domain_lr'},
                            {'label': 'Mini-Batch K-Means Model', 'value': 'domain_minik'}
                        ],
                        value='domain_lr',
                        labelStyle={'display': 'inline-block', 'padding':'20px'}
                    ),
                    dbc.Tooltip(
                        'Selects the model used to cluster job posts into their domains',
                        target='model-selection'
                    )
                ], style={'padding-left':'20px', 'padding-right':'20px'})
            ]),
            dbc.Col([
                dbc.Label([
                    'Filter State:',
                    dcc.Dropdown(
                        id='state-selection',
                        options=[{'label': name, 'value': abbrev} for name, abbrev in zip(states['name'], states['abbrev'])],
                        value=None
                    )
                ], style={'width':'100%'}, id='state-tooltip'),
                dbc.Tooltip(
                    'Filters all charts except "Job Posts by State"',
                    target='state-tooltip'
                )
            ], style={'padding-left':'20px', 'padding-right':'20px'})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Job Posts by Domain", className="card-title"),
                        dcc.Graph(
                            id='domain-barchart',
                            figure=jobs_by_domain_barchart()
                        )
                    ]), style={'margin-bottom':'20px'}
                )
            ]),
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Job Posts by State", className="card-title"),
                        dcc.Graph(
                            id='map',
                            figure=jobs_by_state_map(),
                            config={'scrollZoom':False}
                        )
                    ]), style={'margin-bottom':'20px'}
                )
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Top 20 Most Requested Skills", className="card-title"),
                        dcc.Graph(
                            id='skills-barchart',
                            figure=skills_barchart()
                        )
                    ]), style={'margin-bottom':'20px'}
                )
            ]),
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Top 10 Skills Requested by the Top 5 Companies", className="card-title",
                                style={'margin-bottom':'20px'}),
                        dcc.Graph(
                            id='skills-radar-plot',
                            figure=top_company_skills_radar()
                        )
                    ]), style={'margin-bottom':'20px', 'padding-bottom':'20px'}
                )
            ])
        ])
    ])
], style={'background': '#f2f2f2', 'padding-top':'10px', 'padding-bottom':'600px'})

# Updates to dropdown menu and visualizations when filtering by domains ------------------------------------------
@app.callback(
    [dash.dependencies.Output('domain-selection', 'options'),
    dash.dependencies.Output('domain-selection', 'value')],
    [dash.dependencies.Input('model-selection', 'value')]
)
def update_domain_list(model):
    return domain_list(model), None

@app.callback(
    dash.dependencies.Output('domain-barchart', 'figure'),
    [dash.dependencies.Input('model-selection', 'value'),
     dash.dependencies.Input('state-selection', 'value')]
)
def update_jobs_by_domain_barchart(model, state):
    return jobs_by_domain_barchart(model, state)

@app.callback(
    dash.dependencies.Output('skills-barchart', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value'),
     dash.dependencies.Input('model-selection', 'value'),
     dash.dependencies.Input('state-selection', 'value')]
)
def update_skills_barchart(domain, model, state):
    return skills_barchart(domain, model, state)

@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value'),
     dash.dependencies.Input('model-selection', 'value')]
)
def update_map(domain, model):
    return jobs_by_state_map(domain, model)

@app.callback(
    dash.dependencies.Output('skills-radar-plot', 'figure'),
    [dash.dependencies.Input('domain-selection', 'value'),
     dash.dependencies.Input('model-selection', 'value'),
     dash.dependencies.Input('state-selection', 'value')]
)
def update_radar_plot(domain, model, state):
    return top_company_skills_radar(domain, model, state)
