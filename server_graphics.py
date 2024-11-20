import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np

def user_generator(mean_value = 0, probability = 1):
    t = 0
    while True:
        if probability > np.random.rand():
            zs = np.random.normal(loc=mean_value, scale=1.0, size=100)
            t += 1
            yield zs, t * np.ones_like(zs)
        else: 
            yield None


# Генератор данных
def data_generator():
    users = {
            "user1": user_generator(mean_value=0.0),
            "user2": user_generator(mean_value=5.0, probability = 0.5),
            "user3": user_generator(mean_value=10.0, probability = 0.7),
        }
    for data_tuple in zip(*users.values()):
        data = {user : values for user, values in zip(users, data_tuple) if values is not None}
        yield data



# Создание генератора данных
generator = data_generator()






class DashBoard:
    def __init__(self):
        # Инициализация Dash-приложения
        self.app = dash.Dash(__name__)
        self.make_layout()
        self.define_callbacks()

    
    def make_layout(self):
        """
        Макет приложения
        """
        self.app.layout = html.Div(children=[
            # All elements from the top of the page
            dcc.Store(id='data-store', storage_type='session'),
            html.Div([
                html.H1(children='Server_graphics SNcoincidence test'),

                html.Div(children='''
                    Dash: A web application framework for Python.
                '''),  
            ]),

            html.Div([
                dcc.Graph(id='box-plots'),  # Один график для всех "ящиков с усами"
                dcc.Interval(id='interval-component', interval=5000, n_intervals=0)  # Обновление каждые 1 сек
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
            [State('data-store', 'data')],
            [Input('data_update_button', 'n_clicks')]            
        )(self.update_data)

        @self.app.callback(
            Output('box-plots', 'figure'),
            Input('data-store', 'data'),
        )
        def update_graph(data):
            # self.update_data()

            color_list = {
                "user1": "red",
                "user2": "green",
                "user3": "blue"
            }
            
            # Список для хранения "ящиков с усами" для каждого userID
            box_plots = []
            print(data)
            for userID in data["z"]:
                zs = data["z"][userID]
                ts = data["t"][userID]
                zs = np.concatenate(zs)
                ts = np.concatenate(ts)
                box_plots.append(go.Box(
                    y=zs,
                    x=ts,  
                    name=f'User {userID}',
                    boxpoints=False,
                    marker_color=color_list[userID]
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
        
    def update_data(self, current_data, *args):
       
        data = current_data or {"z": {}, "t": {}}
        new_data:dict = next(generator)

        for userID, values in new_data.items():
            zs, ts = values
            data["z"].setdefault(userID, [])
            data["z"][userID].append(zs)
            data["t"].setdefault(userID, [])
            data["t"][userID].append(ts)

        return data








dashboard = DashBoard()
# Запуск приложения
if __name__ == '__main__':
    dashboard.app.run_server(debug=True)
