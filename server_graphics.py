import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from sn_combine import Buffer
from threading import Thread


class DashBoard(Buffer):
    def __init__(self):
        super().__init__()
        # Инициализация Dash-приложения
        self.app = dash.Dash(__name__)
        self.make_layout()
        self.define_callbacks()
        t = Thread(target=self.app.run_server,
                    kwargs={"debug" : True, "use_reloader" :False})
        t.start()

    
    def make_layout(self):
        """
        Макет приложения
        """
        self.app.layout = html.Div(children=[
            # All elements from the top of the page
            dcc.Store(id='data-store', storage_type='session'),
            html.Div([
                html.H1(children='Server_graphics SNcoincidence test')
            ]),

            html.Div([
                dcc.Graph(id='box-plots'), 
                dcc.Interval(id='interval-component', interval=500, n_intervals=0)  # Обновление каждые 0.5 сек
            ]),

            html.Div([
                html.Button(id='data_update_button', n_clicks=0, children='Update')
            ])

        ])
        
    
    def define_callbacks(self):
        """
        Функция для обновления графиков
        """
        


        self.app.callback(
            Output('data-store', 'data'),
            [Input('data_update_button', 'n_clicks'),
            Input('interval-component', 'n_intervals')]     
        )(self.update_data)

        @self.app.callback(
            Output('box-plots', 'figure'),
            Input('data-store', 'data'),
        )
        def update_graph(data):
            # self.update_data()
            if data == {}:
                return no_update
            
            # Список для хранения "ящиков с усами" для каждого userID
            box_plots = []
            
            for userID in data:
                zs, ts = data[userID]
                box_plots.append(go.Scatter(
                    y=zs,
                    x=ts,  
                    name=f'User {userID}',
                    # boxpoints=False,
                    # marker_color=color_list[userID]
                ))

            # Создание фигуры с несколькими ящиками
            fig = go.Figure(data=box_plots)


            # Настройка осей и заголовков
            fig.update_layout(
                title='Обновляющиеся ящики с усами для каждого userID',
                xaxis_title='Time (ts)',
                yaxis_title='Values (zs)',
            )

            return fig
        
    def update_data(self, *args):      
        return self.get_data()








