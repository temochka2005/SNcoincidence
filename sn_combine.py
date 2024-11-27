import numpy as np
import datetime
from snap.datablock import DataBlock

async def generator(userID: str, shift = 0.0):
    while(True):
        t = datetime.datetime.now()
        z = np.random.normal(loc=float(shift), scale=1.0, size=None)
        yield {"t":t, "z":z, "userID":userID}


class Buffer:
    def __init__(self):
        self.clients = {}

    async def put(self, data:DataBlock):
        if data.id in self.clients:
            self.clients[data.id]+=data
        else:
            self.clients[data.id]=data

    async def get(self):
        return self.get_data()
    
    def get_data(self):
        return list(self.clients.values())