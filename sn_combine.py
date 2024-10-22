import numpy as np
import datetime
import plotext as plt

async def generator(userID: str):
    while(True):
        t = datetime.datetime.now()
        z = np.random.normal(loc=0.0, scale=1.0, size=None)
        yield {"t":t, "z":z, "userID":userID}


class ClientBuffer:
    def __init__(self):
        self.clear()

    def append(self, z, t):
        self.z.append(z)
        self.t.append(t)

    def clear(self):
        self.z = np.array()
        self.t = np.array()

    def len(self):
        return(len(z))

class Buffer:
    def __init__(self):
        self.clear()

    def append(self, z, t, userID):
        buf = self.clients.setdefault(userID, default = ClientBuffer())
        buf.append(z, t)

    def clear(self):
        self.clients = dict()

    def get(self):
        pass 

    
def buffer(size=100):
    async def _buffer(source):
        buffer = Buffer()
        data = []
        time = []
        cnt = 0
        async for t,z in source:
            data.append(z)
            time.append(t)
            cnt += 1
            if cnt == size:
                yield np.asarray(data), time[0], time[-1]
                data = []
                time = []
                cnt = 0
    return _buffer

def plot_hist(data: list):
    plt.cld()
    plt.clf()
    plt.hist(data, bins = 20)
    plt.show()

def plot_box():
    async def _plot_box(source):
        zs = []
        ts = []
        async for data in source:
            z,t0,t1 = data #unpack data
            
            zs.append(z)
            ts.append( datetime.datetime.fromtimestamp((t1.timestamp() + t0.timestamp()) / 2 ) )
            # plotting
            plt.cld()
            plt.clf()
            plt.box(plt.datetimes_to_strings(ts, 'x X'), zs)
            plt.show()
            yield None
    return _plot_box




