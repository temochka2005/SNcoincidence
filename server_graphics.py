import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np




# Предопределенные временные метки, для которых user3 никогда не будет получать данные
missing_ts_for_user3 = {2, 4, 6}  # Например, никогда не будет данных для t = 2, 4, 6

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


# Инициализация Dash-приложения
app = dash.Dash(__name__)

# Макет приложения
app.layout = html.Div([
    dcc.Graph(id='box-plots'),  # Один график для всех "ящиков с усами"
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Обновление каждые 1 сек
])

zs_data = {}
ts_data = {}

# Функция для обновления графиков
@app.callback(
    Output('box-plots', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    # Получение новых данных из генератора
    data:dict = next(generator)
    
    # Обработка данных для каждого пользователя
    for userID, values in data.items():
            zs_data.setdefault(userID, [])
            ts_data.setdefault(userID, [])
            zs, ts = values
            zs_data[userID].append(zs)
            ts_data[userID].append(ts)

    color_list = {
        "user1": "red",
        "user2": "green",
        "user3": "blue"
    }
    
    # Список для хранения "ящиков с усами" для каждого userID
    box_plots = []
    
    for userID in zs_data:
        zs = zs_data[userID]
        ts = ts_data[userID]
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

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
