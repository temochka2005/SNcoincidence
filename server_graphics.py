import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State
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
        self.app.layout = html.Div(children=[
            dcc.Store(id='data-store', storage_type='session'),
            dcc.Store(id='last-update'),
            
            html.Div([
                html.H1(children='Server_graphics SNcoincidence test')
            ]),
            
            # Блок с графиком и интервалами
            html.Div([
                dcc.Graph(id='box-plots'), 
                dcc.Interval(
                    id='interval-component_data', 
                    interval=500,  # Обновление каждые 0.5 сек
                    n_intervals=0
                ),
                dcc.Interval(
                    id='interval-component_ui', 
                    interval=500,  # Обновление каждые 0.1 сек
                    n_intervals=0
                )
            ]),
            
            # Добавляем кнопку (уже была) и ниже - наш переключатель
            html.Div([
                html.Button(
                    id='data_update_button', 
                    n_clicks=0, 
                    children='Update'
                ),
                html.Label("Скользящее окно (48 ч):"),
                dcc.Checklist(
                    id='sliding-window-toggle',
                    options=[{'label': 'Вкл', 'value': 'ON'}],
                    value=[],  # изначально переключатель выключен
                    labelStyle={'display': 'inline-block', 'marginLeft': '10px'}
                )
            ])
        ])

        
    def define_callbacks(self):
        """
        Функция для обновления графиков
        """
        self.app.callback(
            Output('data-store', 'data'),
            Input('interval-component_data', 'n_intervals'),     
        )(self.update_data)

        @self.app.callback(
            Output('box-plots', 'figure'),
            [
                Input('interval-component_ui', 'n_intervals'),
                Input('data-store', 'data'),
                Input('sliding-window-toggle', 'value'),
            ]
        )
        def update_figure(_, data, toggle_value):
            """
            Единый колбэк, который и строит график на основе `data`, 
            и накладывает "скользящее окно" 48 ч, если checkbox включён
            """
            if not data:
                # Если данных нет, возвращаем no_update или пустую фигуру
                return dash.no_update

            # 1) Формируем Plotly-график из data
            traces = []
            for datablock in data:
                # x_vals = list(map(datetime.datetime.fromtimestamp, datablock["ts"]))
                x_vals = datablock["ts"]
                traces.append(go.Scatter(
                    x=x_vals,
                    y=datablock["zs"],
                    name=f'User {datablock["id"]}',
                ))
            fig = go.Figure(data=traces)

            # 2) Общие настройки
            fig.update_layout(
                uirevision='constant', 
                title='Обновляющиеся данные для каждого userID',
                xaxis_title='Time (ts)',
                yaxis_title='Values (zs)',
            )
            
            # 3) Включаем/выключаем "скользящее окно"
            if 'ON' in toggle_value:
                # «Фиксируем» ось X: текущие 48 часов
                now_ts = datetime.datetime.now().timestamp()
                tmin = datetime.datetime.fromtimestamp(now_ts - 15)
                tmax = datetime.datetime.fromtimestamp(now_ts)
                
                fig.update_xaxes(
                    autorange=False,
                    range=[tmin, tmax],
                    tickformat='%Y-%m-%d %H:%M:%S'
                )
            else:
                # Возвращаемся к авторесайзу
                fig.update_xaxes(
                    autorange=True,
                    tickformat='%Y-%m-%d %H:%M:%S'
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
