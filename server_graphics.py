import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from threading import Thread
from sn_combine import Buffer
from snap.datablock import DataBlock

import datetime  # <-- (Новая строка) понадобится для обработки времени

class DashBuffer(Buffer):
    def __init__(self, drop_tail_hours=1/60):  # <-- (Изменено) добавлен параметр drop_tail_hours
        super().__init__()
        self.drop_tail_hours = drop_tail_hours  # <-- (Новая строка) запоминаем, сколько часов держать
        
        # Инициализация Dash-приложения
        self.app = dash.Dash(__name__)
        self.make_layout()
        self.define_callbacks()
        t = Thread(
            target=self.app.run_server,
            kwargs={"debug": True, "use_reloader": False}
        )
        t.start()

    def make_layout(self):
        """
        Макет приложения
        """
        self.app.layout = html.Div(children=[
            dcc.Store(id='data-store', storage_type='session'),
            html.Div([
                html.H1(children='Server_graphics SNcoincidence test')
            ]),

            html.Div([
                dcc.Graph(id='box-plots'), 
                dcc.Interval(
                    id='interval-component', 
                    interval=500,  # Обновление каждые 0.5 сек
                    n_intervals=0
                )
            ]),

            html.Div([
                html.Button(
                    id='data_update_button', 
                    n_clicks=0, 
                    children='Update'
                )
            ])

        ])
        
    def define_callbacks(self):
        """
        Функция для обновления графиков
        """
        self.app.callback(
            Output('data-store', 'data'),
            [
                Input('data_update_button', 'n_clicks'),
                Input('interval-component', 'n_intervals')
            ]     
        )(self.update_data)

        @self.app.callback(
            Output('box-plots', 'figure'),
            Input('data-store', 'data'),
        )
        def update_graph(data: list[dict]):
            if data == {}:
                return no_update
            
            # Список для хранения "ящиков" (линий) для каждого userID
            box_plots = []

            # Преобразуем float-значения времени в datetime и формируем график
            for datablock in data:
                # <-- (Новая секция) преобразуем ts в datetime:
                x_vals = [
                    datetime.datetime.fromtimestamp(ts_val) 
                    for ts_val in datablock["ts"]
                ]
                box_plots.append(go.Scatter(
                    x=x_vals,
                    y=datablock["zs"],
                    name=f'User {datablock["id"]}',
                ))

            # Создание фигуры
            fig = go.Figure(data=box_plots)

            # Настройка осей и заголовков
            fig.update_xaxes(
                tickformat='%Y-%m-%d %H:%M:%S'  # <-- (Новая строка) формат оси X
            )
            fig.update_layout(
                uirevision='constant',      # <-- (Новая строка) чтобы масштаб не сбрасывался
                title='Обновляющиеся данные для каждого userID',
                xaxis_title='Time (ts)',
                yaxis_title='Values (zs)',
            )

            return fig
    
    # <-- (Новая функция) функция, которая удаляет из self.clients данные старше self.drop_tail_hours
    def drop_tail(self):
        """Удаляем данные старше заданного количества часов."""
        now_ts = datetime.datetime.now().timestamp()
        cutoff = now_ts - self.drop_tail_hours * 3600
        
        # self.clients — это словарь, где ключ: userID, 
        # значение: DataBlock с полями .ts и .zs
        for user_id, block in self.clients.items():
            self.clients[user_id] = block.drop_tail(cutoff)

    def update_data(self, *args):
        # Преобразовываем DataBlock -> dict для хранения в dcc.Store
        def datablock_to_dict(datablock: DataBlock):
            return {
                "id": datablock.id,
                "zs": datablock.zs,
                "ts": datablock.ts
            }
        
        # <-- (Новая строка) сбрасываем хвост перед возвратом
        self.drop_tail()
        
        return list(map(datablock_to_dict, self.get_data()))
