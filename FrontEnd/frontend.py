import dash
import dash_core_components as dcc
import dash_html_components as html
import psycopg2
import pandas as pd
from dash.dependencies import Input, Output
import dash_table as dt

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

#Establish connection to your database
con = psycopg2.connect(host="xxxx",dbname="testing", user="xxxx", password="xxxx")


outline_style = {
    'height': '70px',
    'font-size': '150%'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '8px',
    'fontWeight': 'bold',
}

selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#f5f5f5',#4582c2
    'color': '#abc432',
    'padding': '8px',
    'fontWeight': 'bold',
}

df_lib = pd.read_csv('LibraryCategory.csv')
lib_list = df_lib['Libraries'].values.tolist()

app.layout = html.Div([
    html.H1('Jupyter Trends',style={'text-align': 'left','backgroundColor':'orange','font-size': '400%','padding': '20px',}),

    dcc.Tabs(id="tabs-navigation", value='tab-1', children=[
        dcc.Tab(label = 'Library Trends', value = 'tab-1', style = tab_style, selected_style = selected_style),
        dcc.Tab(label = 'Users recommendation', value = 'tab-2', style = tab_style, selected_style = selected_style),
    ], style = outline_style),
        html.Div(id='tabs-content-inline')
])

@app.callback(
    Output('tabs-content-inline', 'children'),
    [Input('tabs-navigation', 'value')]
)

def render_content(tab):
    
    lib = lib_list[0]
    qry = "select timestamp,SUM(CAST(counts AS int)) as users from countlib WHERE libraries = '" + lib + "' GROUP BY timestamp ORDER BY timestamp ASC"
    df_lib1 = pd.read_sql_query(qry,con)
    #df_lib1.show(5)

	#Tab 1 to show trends in top 10 libraries
    if tab == 'tab-1':
        return html.Div([
            html.H4('Choose Library',style={'text-align': 'center','padding': '20px 0px 0px 0px'}),
        

                html.Div([
                dcc.Dropdown(
                    id='choose-library',
                    options=[{'label': i, 'value': i} for i in lib_list],
                    value='numpy',
                    clearable=False,
                ),
            ],
            style={'width': '50%', 'text-align': 'center','marginLeft': '25%','display': 'inline-block','fontWeight': 'bold','fontsize':'120%'}),
         
            dcc.Graph(
                id='graph-1-tabs',
                figure={
                    'data': [
                    {'x': df_lib1['timestamp'], 'y': df_lib1['users'], 'type': 'line', 'name': lib_list[0]},
                    ],
                    'layout':{
                            'xaxis':{
                                'title':'Date',
                                },
                            'yaxis':{
                                'title':'Users',
                                },
                            'font': dict(
                                size=18,
                            ),
                    }
                }, style={'height': '600px'}
            )
        ], style={'marginLeft': '5%', 'marginRight': '5%'})

    #Tab 2 to display recommended github users
    if tab == 'tab-2':
        return html.Div([
                html.Div([
                html.H4('Choose Library',style={'text-align': 'center','padding': '20px 0px 0px 0px'}),
                
                html.Div([
                    dcc.Dropdown(
                        id='choose-library',
                        options=[{'label': i, 'value': i} for i in lib_list],
                        value='numpy',
                        clearable=False,
                    ),
                ]),
            ],style={'width': '50%', 'text-align': 'center','marginLeft': '25%','display': 'inline-block','fontWeight': 'bold','fontsize':'60%'}),
            
            html.Div([
                html.Div([
                        html.H4('Code Modularity: Class'),
                        dcc.Graph(id='g1')
                    ], className="six columns"),

                    html.Div([
                        html.H4('User Table Links'),
                        dt.DataTable(
                                    id='table1',
                                    columns=[
                                    {'name': 'users', 'id': 'users'},
                                    {'name': 'link', 'id': 'link'}],
                                    style_cell={'textAlign': 'left','font-size':'120%'},
                                    style_header={
                                        'font-size': '160%',
                                        #'backgroundColor': 'white',
                                        'fontWeight': 'bold',
                                        'backgroundColor': 'orange'
                                    },
                                    data=[
                                        {'users': i, 'link': i} for i in range(5)],)
                    ],className="six columns"),
                ], className="row"),
            
            html.Div([
                html.Div([
                        html.H4('Code Modularity: Functions'),
                        dcc.Graph(id='g2')
                    ], className="six columns"),

                    html.Div([
                        html.H4('User Table Links'),
                        dt.DataTable(
                                    id='table2',
                                    columns=[
                                    {'name': 'users', 'id': 'users'},
                                    {'name': 'link', 'id': 'link'}],
                                    style_cell={'textAlign': 'left','font-size':'120%'},
                                    style_header={
                                        'font-size': '160%',
                                        #'backgroundColor': 'white',
                                        'fontWeight': 'bold',
                                        'backgroundColor': 'orange',
                                    },
                                    data=[
                                        {'users': i, 'link': i} for i in range(5)],)
                    ],className="six columns"),
                ], className="row"),

            html.Div([
                html.Div([ 
                        html.H4('Code Modularity: Comments'),
                        dcc.Graph(id='g3')
                    ], className="six columns"),

                    html.Div([
                        html.H4('User Table Links'),
                        dt.DataTable(
                                    id='table3',
                                    columns=[
                                    {'name': 'users', 'id': 'users'},
                                    {'name': 'link', 'id': 'link'}],
                                    style_cell={'textAlign': 'left','font-size':'120%'},
                                    style_header={
                                        'font-size': '160%',
                                        #'backgroundColor': 'white',
                                        'fontWeight': 'bold',
                                        'backgroundColor': 'orange',
                                    },
                                    data=[
                                        {'users': i, 'link': i} for i in range(5)],)
                    ],className="six columns"),
                ], className="row"),

            html.Div([
                html.Div([
                       # html.A(children='Please click this link', id='link',href='https://dash.plot.ly', target='_blank')
                        html.H4('Code Modularity: Class'),
                        dcc.Graph(id='g4')
                    ], className="six columns"),

                    html.Div([
                        html.H4('User Table Links'),
                        dt.DataTable(
                                    id='table4',
                                    columns=[
                                    {'name': 'users', 'id': 'users'},
                                    {'name': 'link', 'id': 'link'}],
                                    style_cell={'textAlign': 'left','font-size': '120%'},
                                    style_header={
                                        'font-size': '160%',
                                        #'backgroundColor': 'white',
                                        'fontWeight': 'bold',
                                        'backgroundColor': 'orange',
                                    },
                                    data=[
                                        {'users': i, 'link': i} for i in range(5)],)
                    ],className="six columns"),
                ], className="row"),
        ])


@app.callback(
    Output('graph-1-tabs', 'figure'),
    [Input('choose-library', 'value')]
)

def update_graph(lib):

    qry = "select timestamp,SUM(CAST(counts AS int)) as users from countlib WHERE libraries = '" + lib + "' GROUP BY timestamp ORDER BY timestamp ASC"
    df_lib1 = pd.read_sql_query(qry,con)
 
    return {
        'data': [
        {'x': df_lib1['timestamp'], 'y': df_lib1['users'], 'type': 'line', 'name': lib},
        ],
        'layout':{
                'xaxis':{
                    'title':'Date',
                    },
                'yaxis':{
                    'title':'Users',
                    },
                    'font': dict(
                        size=18,
                    ),
        }
    }


@app.callback([Output('g1','figure'),
               Output('table1','data'),
               Output('g2','figure'),
               Output('table2','data'),
               Output('g3','figure'),
               Output('table3','data'),
               Output('g4','figure'),
               Output('table4','data')],
               [Input('choose-library','value')])


def update_figure(library):
    lib = library
    qry = "select a.owner_login as users, max(a.class_count) as classes from (select owner_login, class_count from finalscores inner join libraries on libraries.nb_id = finalscores.nb_id where '" + lib + "' = ANY(libraries.libraries)) a group by a.owner_login ORDER BY 2 DESC LIMIT 5;"
    df_lib5 = pd.read_sql_query(qry,con)
    
    labels = ['users','classes']
    df1 = pd.DataFrame.from_records(df_lib5,columns=labels)
    df1['link'] = 'https://github.com/' + df1['users']
    df1 = df1[['users','link']]
    d = df1['users'].tolist()
    print(d)
    

    qry = "select a.owner_login as users, max(a.class_count) as functions from (select owner_login, class_count from finalscores inner join libraries on libraries.nb_id = finalscores.nb_id where '" + lib + "' = ANY(libraries.libraries)) a group by a.owner_login ORDER BY 2 DESC LIMIT 5;"
    df_lib6 = pd.read_sql_query(qry,con)
    labels = ['users','functions']
    df2 = pd.DataFrame.from_records(df_lib6,columns=labels)
    df2['link'] = 'https://github.com/' + df2['users']
    df2 = df2[['users','link']]
    d = df2['users'].tolist()
    


    qry = "select a.owner_login as users, max(a.comment_count) as comments from (select owner_login, comment_count from finalscores inner join libraries on libraries.nb_id = finalscores.nb_id where '" + lib + "' = ANY(libraries.libraries)) a group by a.owner_login ORDER BY 2 DESC LIMIT 5;"
    df_lib7 = pd.read_sql_query(qry,con)
    labels = ['users','comments']
    df3 = pd.DataFrame.from_records(df_lib7,columns=labels)
    df3['link'] = 'https://github.com/' + df3['users']
    df3 = df3[['users','link']]
    d = df3['users'].tolist()
    


    qry = "select a.owner_login as users, max(a.lines_of_code) as lines from (select owner_login, lines_of_code from finalscores inner join libraries on libraries.nb_id = finalscores.nb_id where '" + lib + "' = ANY(libraries.libraries)) a group by a.owner_login ORDER BY 2 DESC LIMIT 5;"
    df_lib8 = pd.read_sql_query(qry,con)
    labels = ['users','lines']
    df4 = pd.DataFrame.from_records(df_lib8,columns=labels)
    df4['link'] = 'https://github.com/' + df4['users']
    df4 = df4[['link','users']]
    d = df4['users'].tolist()
    

    return [
            {'data': [{'x': df_lib5['users'], 'y': df_lib5['classes'], 'type': 'bar','name': lib}],'layout':{ 'xaxis':{ 'title':'Recommended Users' }, 'yaxis':{ 'title':'Class Count'} }},\
            df1.to_dict('records'),    
            {'data': [{'x': df_lib6['users'], 'y': df_lib6['functions'], 'type': 'bar','name': lib}],'layout':{ 'xaxis':{ 'title':'Recommended Users' }, 'yaxis':{ 'title':'Function Count'} }},\
            df2.to_dict('records'),
            {'data': [{'x': df_lib7['users'], 'y': df_lib7['comments'], 'type': 'bar','name': lib}],'layout':{ 'xaxis':{ 'title':'Recommended Users' }, 'yaxis':{ 'title':'Comment Count'} }},\
            df3.to_dict('records'),
            {'data': [{'x': df_lib8['users'], 'y': df_lib8['lines'], 'type': 'bar','name':lib}],'layout':{ 'xaxis':{ 'title':'Recommended Users' }, 'yaxis':{ 'title':'Lines of Code Count'} }},\
            df4.to_dict('records')]


if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0",port=80)


