import dash_bootstrap_components as dbc 
import dash_html_components as html 
import dash_core_components as dcc 
import dash_auth
import plotly.express as px  
import pandas as pd
import dash
import requests
import os

from dash.dependencies import Input, Output

# Récupération des identifiants de connection
s3 = {'jeankev', 'olol'}

# Création de l'application dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.config['suppress_callback_exceptions'] = True
server = app.server

# authentification au dashboard
auth = dash_auth.BasicAuth(app, s3)

# Mise en forme de l'application
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-viz', children=[
        dcc.Tab(label='Visualisation', value='tab-viz'),
        dcc.Tab(label='Update/Delete', value='tab-update'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def tab_content(tab):
    if tab == 'tab-viz':
        content = html.Div([dbc.Row([
            dbc.Col(dcc.Dropdown(id='filiere', options=[{'label': i, 'value' : i} for i in requests.get('https://api-energie.herokuapp.com/api/dash?filiere=all').json()['data']], placeholder='Filière', value=None)),
            dbc.Col(dcc.Dropdown(id='region', options=[{'label': i, 'value' : i} for i in requests.get('https://api-energie.herokuapp.com/api/dash?region=all').json()['data']], placeholder='Région', value=None)),
            dbc.Col(dcc.Dropdown(id='dptmt', options=[{'label': i, 'value' : i} for i in requests.get('https://api-energie.herokuapp.com/api/dash?dptmt=all').json()['data']], placeholder='Département', value=None)),
            dbc.Col(dcc.Dropdown(id='commune', options=[{'label': i, 'value' : i} for i in requests.get('https://api-energie.herokuapp.com/api/dash?commune=all').json()['data']], placeholder='Commune', value=None)),
            dbc.Col(dcc.Dropdown(id='operateur', options=[{'label': i, 'value' : i} for i in requests.get('https://api-energie.herokuapp.com/api/dash?operateur=all').json()['data']], placeholder='Opérateur', value=None)),
        ], style={'width':'80%', 'margin':'2em auto', 'min-height':'40px'}),
            dbc.Row([
                dbc.Label("Configuration des données:", style={'margin-right':'2em'}),
                dbc.RadioItems(options=[{"label":"Informations", "value":1}, {"label":"Consommation totale", "value":2}], 
                value=1, id="radio-items", inline=True)
            ], style={'width':'70%'}, justify='center'),
            html.Div(id='radio-info', style={'width':'80%', 'margin':'1em auto', 'text-align':'center', 'min-height':'25px'}),
            html.Div(id='json-content', 
            style={'width':'80%', 'margin':'3em auto', 'text-align':'center', 'border':'solid 2px black', 'border-radius':'25px', 'min-height':'25em'}),
            html.Div(dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3("Version allégée", className='card-title', style={'margin-bottom':'0.5em', 'color':'black'}),
                    html.H6("Informations essentielles", className='card-subtitle', style={'margin-bottom':'2em'}),
                    html.P("recordid, filiere, commune, conso, operateur", className='card-text'),
                    dbc.Button("Télécharger", id='dl-btn-light', outline=True, color="success", className='mr-1', style={'margin-top':'2em', 'margin-bottom':'1em'}),
                ], style={'padding':'4em', 'height':'25em'}))),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3("Version Complète", className='card-title', style={'margin-bottom':'0.5em', 'color':'black'}),
                    html.H6("Toutes les informations", className='card-subtitle', style={'margin-bottom':'2em'}),
                    html.P("recordid, filiere, conso, region, département, commune, conso, année, epci, naf, iris...", className='card-text'),
                    dbc.Button("Télécharger", id='dl-btn-full', outline=True, color="success", className='mr-1', style={'margin-top':'2em', 'margin-bottom':'1em'}),
                ], style={'padding':'4em', 'height':'25em'})))
            ], justify='center'), style={'width':'60%', 'text-align':'center', 'margin':'0 auto'}),
            html.Div(id='dl-content', style={'width':'80%', 'margin':'1em auto', 'text-align':'center'}),
        ])
        return content
    elif tab == 'tab-update':
        content = html.Div([
            dbc.Row([
                dbc.Col(dbc.FormGroup([
                    dbc.Label("Renseignez l'identifiant de l'objet à modifier/supprimer"),
                    dbc.Input(type='text', id='record-id', placeholder='e.g. d903684b59df6b97719b29bdeab1447c597a83d7', bs_size='lg'),
                ]))
            ]),
            dbc.Row([
                dbc.Col(dbc.FormGroup([
                    dbc.Label("Filière"),
                    dbc.Input(type='text', id='filiere-hnd', placeholder='e.g. Electricité', value=None),
                ])),
                dbc.Col(dbc.FormGroup([
                    dbc.Label("Secteur"),
                    dbc.Input(type='text', id='secteur-hnd', placeholder='e.g. Tertiaire', value=None),
                ]))
            ]),
            dbc.Row([
                dbc.Col(dbc.FormGroup([
                    dbc.Label("Opérateur"),
                    dbc.Input(type='text', id='operateur-hnd', placeholder='e.g. Enedis', value=None),
                ])),
                dbc.Col(dbc.FormGroup([
                    dbc.Label("Consommation"),
                    dbc.Input(type='float', id='conso-hnd', placeholder='e.g. 439.01791671231', value=None),
                ]))
            ]),
            dbc.Row([
                    dbc.Button("Modifier", id='upd-hnd', style={'font-size':'1.5em', 'margin':'25px 1em'}),
                    dbc.Button("Supprimer", id='del-hnd', style={'font-size':'1.5em', 'margin':'25px 1em'}),
            ], style={'margin':'0 auto', 'display':'flex', 'justify-content':'center', 'align-items':'center'}),
            html.P(id='submit-content', style={'margin':'0 auto', 'text-align':'center'}),
        ], style={'width':'60%', 'margin':'3em auto'})
        return content

@app.callback(Output('filiere', 'options'), 
    [Input('region', 'value'), Input('dptmt', 'value'), Input('commune', 'value'), Input('operateur', 'value')])
def set_filiere_opt(region, dptmt, commune, operateur):
    return [{'label':i, 'value':i} for i in requests.get(f'https://api-energie.herokuapp.com/api/dash?filiere=all&region={region}&dptmt={dptmt}&commune={commune}&operateur={operateur}').json()['data']]

@app.callback(Output('region', 'options'), [Input('filiere', 'value'), Input('dptmt', 'value'), Input('commune', 'value'), Input('operateur', 'value')])
def set_region_opt(filiere, dptmt, commune, operateur):
    return [{'label':i, 'value':i} for i in requests.get(f'https://api-energie.herokuapp.com/api/dash?filiere={filiere}&region=all&dptmt={dptmt}&commune={commune}&operateur={operateur}').json()['data']]

@app.callback(Output('dptmt', 'options'), [Input('filiere', 'value'), Input('region', 'value'), Input('commune', 'value'), Input('operateur', 'value')])
def set_dptmt_opt(filiere, region, commune, operateur):
    return [{'label':i, 'value':i} for i in requests.get(f'https://api-energie.herokuapp.com/api/dash?filiere={filiere}&region={region}&dptmt=all&commune={commune}&operateur={operateur}').json()['data']]

@app.callback(Output('commune', 'options'), [Input('filiere', 'value'), Input('region', 'value'), Input('dptmt', 'value'), Input('operateur', 'value')])
def set_commune_opt(filiere, region, dptmt, operateur):
    return [{'label':i, 'value':i} for i in requests.get(f'https://api-energie.herokuapp.com/api/dash?filiere={filiere}&region={region}&dptmt={dptmt}&commune=all&operateur={operateur}').json()['data']]

@app.callback(Output('operateur', 'options'), [Input('filiere', 'value'), Input('region', 'value'), Input('dptmt', 'value'), Input('commune', 'value')])
def set_operateur_opt(filiere, region, dptmt, commune):
    return [{'label':i, 'value':i} for i in requests.get(f'https://api-energie.herokuapp.com/api/dash?filiere={filiere}&region={region}&dptmt={dptmt}&commune={commune}&operateur=all').json()['data']]

@app.callback(Output('radio-info', 'children'), Input('radio-items', 'value'))
def set_radio_items(radio):
    if radio == 1:
        pass
    elif radio == 2:
        return html.P("Vous n'aurez que la consommation totale lors du téléchargement.", style={'font-weight':'bold'})

@app.callback(Output('json-content', 'children'), [Input('filiere', 'value'), Input('region', 'value'), Input('dptmt', 'value'), Input('commune', 'value'), Input('operateur', 'value'), Input('radio-items', 'value')])
def set_json_content(filiere, region, dptmt, commune, operateur, radio):
    if filiere != None or region != None or dptmt != None or commune != None or operateur != None:
        if radio == 1:
            return html.Div([
                html.P(f'{requests.get(f"https://api-energie.herokuapp.com/api/nrg?filiere={filiere}&region={region}&dptmt={dptmt}&commune={commune}&operateur={operateur}").json()["data"][:10]}'),
                ], style={'padding':'2em'})
        elif radio == 2:
            return html.Div([
                dcc.Graph(id='conso-graph', figure=get_graph(region, dptmt, commune)),
                ], style={'padding':'2em'})

@app.callback(Output('dl-content', 'children'), [Input('dl-btn-light', 'n_clicks'), Input('dl-btn-full', 'n_clicks'), Input('filiere', 'value'), Input('region', 'value'), Input('dptmt', 'value'), Input('commune', 'value'), Input('operateur', 'value'), Input('radio-items', 'value')])
def dl_json_file(btn_light, btn_full, filiere, region, dptmt, commune, operateur, radio):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dl-btn-light' in changed_id:
        if radio == 1:
            save_json(f'{requests.get(f"https://api-energie.herokuapp.com/api/nrg?filiere={filiere}&region={region}&dptmt={dptmt}&commune={commune}&operateur={operateur}").json()}')  
            return html.P('Données bien téléchargées. Version allégée.')
        elif radio == 2:
            return [html.P("La version allégée n'existe pas pour la consommation totale."),
                    html.P("Veuillez choisir la version complète vou changez de configuration des données.")]
    elif 'dl-btn-full' in changed_id:
        if radio == 1:
            save_json(f'{requests.get(f"https://api-energie.herokuapp.com/api/nrg?filiere={filiere}&region={region}&dptmt={dptmt}&commune={commune}&operateur={operateur}&complete=True").json()}')
            return html.P('Données bien téléchargées. Version complète.')
        elif radio == 2:
            save_json(f'{requests.get(f"https://api-energie.herokuapp.com/api/tot?filiere={filiere}&region={region}&dptmt={dptmt}&commune={commune}&operateur={operateur}&complete=True").json()}')
            return html.P('Données de consommation totale bien téléchargées.')
    else:
        return html.P('')

@app.callback(Output('submit-content', 'children'), [Input('upd-hnd', 'n_clicks'), Input('del-hnd', 'n_clicks'), Input('record-id', 'value'), Input('filiere-hnd', 'value'), Input('secteur-hnd', 'value'), Input('operateur-hnd', 'value'), Input('conso-hnd', 'value')])
def modif_post(update_btn, delete_btn, record_id, filiere, secteur, operateur, conso):
    clicked = [p['prop_id'] for p in dash.callback_context.triggered][0]
    rslt = ''
    if 'upd-hnd' in clicked:
        if record_id != None:
            if requests.get(f"https://api-energie.herokuapp.com/api/check?recordid={record_id}").json()['exist'] == True:
                req_str = f"https://api-energie.herokuapp.com/api/upd?recordid={record_id}"
                if filiere != None:
                    req_str += f"&filiere={filiere}"
                if secteur != None:
                    req_str += f"&secteur={secteur}"
                if operateur != None:
                    req_str += f"&operateur={operateur}"
                if conso != None:
                    req_str += f"&conso={conso}"
                requests.put(req_str)
                rslt = f"{record_id} à bien été mis à jour."
            else:
                rslt = "L'identifiant est incorrect."
        else: 
            rslt = "Veuillez préciser un identifiant."
    elif 'del-hnd' in clicked:
        if record_id != None:
            if requests.get(f"https://api-energie.herokuapp.com/api/check?recordid={record_id}").json()['exist'] == True:
                requests.delete(f"https://api-energie.herokuapp.com/api/rmv?recordid={record_id}")
                rslt = f"{record_id} à été retiré."
            else:
                rslt = "L'identifiant est incorrect."
        else: 
            rslt = "Veuillez préciser un identifiant."
    return html.P(rslt)

def save_json(json):
    with open("conso.json", "w") as my_file:
        my_file.write(json)

def get_graph(region, dptmt, commune):
    data_gaz = requests.get(f"https://api-energie.herokuapp.com/api/tot?filiere=Gaz&region={region}&dptmt={dptmt}&commune={commune}").json()
    data_elec = requests.get(f"https://api-energie.herokuapp.com/api/tot?filiere=Electricité&region={region}&dptmt={dptmt}&commune={commune}").json()
    try :
        x_key = list(data_gaz['data'].keys())[-2]
    except :
        x_key = list(data_elec['data'].keys())[-2]
    try :
        x = data_gaz['data'][x_key]
    except :
        x = data_elec['data'][x_key]
    try :
        y_gaz = data_gaz['data']['conso_tot']
    except :
        y_gaz = 0
    try :
        y_elec = data_elec['data']['conso_tot']
    except :
        y_elec = 0
    df = pd.DataFrame({"Localisation":[x, x], "Consommation":[y_elec, y_gaz], "Filière":["Electricité", "Gaz"]})
    fig = px.bar(df, x="Localisation", y="Consommation", color="Filière", barmode='group')
    fig.update_yaxes(title_text='Consommation (en kWh)')
    return fig

# Lancement de l'application
# if __name__ == '__main__':
#     app.run_server(debug=True)