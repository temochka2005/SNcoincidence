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
                    interval=100,  # Обновление каждые 0.1 сек
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
            Output('box-plots', 'figure', allow_duplicate=True),
            Input('data-store', 'data'),
            prevent_initial_call=True
        )
        def update_graph(data: list[dict]):
            if data == {}:
                return no_update
            
            # Список для хранения "ящиков" (линий) для каждого userID
            box_plots = []
            # current_time = datetime.datetime.now().timestamp()
            # Преобразуем float-значения времени в datetime и формируем график
            for datablock in data:
                # <-- (Новая секция) преобразуем ts в datetime:
                x_vals = list(map(datetime.datetime.fromtimestamp, datablock["ts"]))
                box_plots.append(go.Scatter(
                    x=x_vals,
                    y=datablock["zs"],
                    name=f'User {datablock["id"]}',
                ))

            # Создание фигуры
            fig = go.Figure(data=box_plots)
            # Настройка осей и заголовков
            fig.update_xaxes(
                tickformat='%Y-%m-%d %H:%M:%S',
                range=[None, 0],
                autorange=True  # <-- (Новая строка) формат оси X
            )
            fig.update_layout(
                uirevision='constant',      # <-- (Новая строка) чтобы масштаб не сбрасывался
                title='Обновляющиеся данные для каждого userID',
                xaxis_title='Time (ts)',
                yaxis_title='Values (zs)',
            )

            return fig

        @self.app.callback(
            [   # Выходы
                Output('box-plots', 'figure'),
                Output('last-update', 'data')
            ],
            [   # Входы
                Input('interval-component_ui', 'n_intervals'),
                Input('sliding-window-toggle', 'value')
            ],
            [   # Состояния
                State('box-plots', 'figure'),
                State('last-update', 'data')
            ]
        )
        def update_ui(_, toggle_value, figure, last_update):
            """
            Колбэк, который раз в 0.1 сек обновляет ось X, если включён режим 
            "скользящее окно".
            """
            current_time = datetime.datetime.now().timestamp()
            
            # Если это первое срабатывание -- просто зафиксируем время.
            if last_update is None:
                return figure, current_time
            
            # Проверяем, включён ли наш переключатель.
            # Если в toggle_value лежит 'ON', значит пользователь включил "скользящее окно".
            if 'ON' in toggle_value:
                # Выключаем autorange:
                figure['layout']['xaxis']['autorange'] = False
                
                # Задаём правую границу как "текущее время", а левую - за 48 ч до него.
                tmin = datetime.datetime.fromtimestamp(current_time - 15)
                tmax = datetime.datetime.fromtimestamp(current_time)
                
                # Прописываем фиксированный диапазон [tmin, tmax].
                figure['layout']['xaxis']['range'] = [tmin, tmax]
            else:
                # Возвращаемся к режиму авторесайза по X:
                figure['layout']['xaxis']['autorange'] = True
                # Удаляем ключ 'range', чтобы plotly не оставлял старое значение.
                if 'range' in figure['layout']['xaxis']:
                    del figure['layout']['xaxis']['range']

            return figure, current_time

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
