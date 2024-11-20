import numpy as np
import datetime
import plotext as plt

async def generator(userID: str, shift = 0.0):
    while(True):
        t = datetime.datetime.now()
        z = np.random.normal(loc=float(shift), scale=1.0, size=None)
        yield {"t":t, "z":z, "userID":userID}


class ClientBuffer:
    def __init__(self):
        self.clear()

    def put(self, z, t):
        self.z = np.append(self.z, z)
        self.t = np.append(self.t, t)

    def clear(self):
        self.z = np.array([])
        self.t = np.array([])

    def len(self):
        return(len(self.z))

    def get(self):
        if len(self.z) != 0:
            return self.z, self.t
        else: 
            pass

class Buffer:
    def __init__(self):
        self.clear()

    async def put(self, data):
        buf = self.clients.setdefault(data["userID"], ClientBuffer())
        buf.put(data["z"], data["t"])

    def clear(self):
        self.clients = dict()

    async def get(self):
        return self.get_data()
    
    def get_data(self):
        result = dict()
        for userID in self.clients:
            result[userID] = self.clients[userID].get()
        return result
            
            



    
def buffer(size=100):
    async def _buffer(source):
        buffer = ClientBuffer()
        async for data in source:
            buffer.put(z = data['z'], t = data['t'])
            if buffer.len() == size:
                yield buffer.get()
                buffer.clear()
                
    return _buffer

def plot_hist(data: list):
    plt.cld()
    plt.clf()
    plt.hist(data, bins = 20)
    plt.show()

def plot_box():
    async def _plot_box(source):
        zs = dict()
        ts = dict()
        
        async for data in source:
            for userID in data:
                client_data = data[userID]
                if client_data:
                    z,t0,t1 = data[userID] #unpack data 
                    zs.setdefault(userID, []).append(z)
                    ts.setdefault(userID, []).append( datetime.datetime.fromtimestamp((t1.timestamp() + t0.timestamp()) / 2 ) )
            # plotting
            plt.cld()
            plt.clf()
            for userID in zs:
                plt.box(plt.datetimes_to_strings(ts[userID], 'x X'), zs[userID])
            plt.show()
            yield None
    return _plot_box






import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
       


async def boxes_calculator(source):
    zs = dict()
    ts = dict()
    box_plots= []
    async for data in source:
        for userID in data:
            client_data = data[userID]
            if client_data:
                z,t0,t1 = data[userID] #unpack data
                zs.setdefault(userID, []).append(z)
                ts.setdefault(userID, []).append( datetime.datetime.fromtimestamp((t1.timestamp() + t0.timestamp()) / 2 ) )
                
        for userID in zs:
            box_plots.append(go.Box(
                y=zs[userID],  # Данные для ящика с усами
                x=ts[userID],  # Временная метка x
                name=f'User {userID}',  # Название для каждого ящика
                boxpoints=False,
                # marker_color = color_list[userID]
            ))
    yield box_plots

def Trying_Dash():
    # Инициализация Dash-приложения
    app = dash.Dash(__name__)

    # Макет приложения
    app.layout = html.Div([
        dcc.Graph(id='box-plots'),  # Один график для всех "ящиков с усами"
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Обновление каждые 1 сек
    ])
    
    # Функция для обновления графиков
    @app.callback(
    Output('box-plots', 'figure'),
    [Input('interval-component', 'n_intervals')]
    )
    async def bot_plot(n):  

        box_plots = await boxes_calculator()

        fig = go.Figure(data=box_plots)
        # Настройка осей и заголовков
        fig.update_layout(
            title='Обновляющиеся ящики с усами для каждого userID',
            xaxis_title='Time (ts)',
            yaxis_title='Values (zs)',
        )
            
        return fig

    # Запуск приложения
    if __name__ == '__main__':
        app.run_server(debug=True)

Trying_Dash()