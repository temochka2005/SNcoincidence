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
            return self.z, self.t[0], self.t[-1]
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
        result = dict()
        for userID in self.clients:
            result[userID] = self.clients[userID].get()
            self.clients[userID].clear()
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




