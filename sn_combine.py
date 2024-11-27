import numpy as np
import datetime

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