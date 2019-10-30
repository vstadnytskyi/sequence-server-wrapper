#!/usr/bin/env python3
"""
Authors: Valentyn Stadnytskyi
Date created: 23 Oct 2019
Date last modified: 25 Oct 2019
Python Version: 3

Description:
------------
The Template Server hosts three PVs: CMD(command PV), ACK(acknowledgement PV) and values PV.
"""

from logging import debug,info,warning,error
#Input/Output server library
from caproto.server import pvproperty, PVGroup, SubGroup, ioc_arg_parser, run
#from ubcs_auxiliary.threading import new_thread
from numpy import nan

class Server(PVGroup):
    #placeholder for the self.system attribute
    system = None

    # define relavant PVs.
    CMD = pvproperty(value='This is command string', max_length = 10000, dtype = str)
    ACK = pvproperty(value=0, read_only = True)
    message = pvproperty(value='0', read_only = True, dtype = str)
    values = pvproperty(value=[nan,nan], read_only = True, max_length = 10000)


    @CMD.startup #this fubction will be executed on instantiaton
    async def CMD(self, instance, async_lib):
        print('* request method called at server startup @CMD.startup')
        self.io_put_queue = async_lib.ThreadsafeQueue()
        if self.system is not None:
            self.system.io_put_queue = self.io_put_queue
        else:
            print(f"@CMD.startup the self.system is {self.system}")
        while True:
            value = await self.io_put_queue.async_get()
            print(f'Got put request from the system group: {value}')
            if 'CMD' in list(value.keys()):
                await self.CMD.write(value['CMD'])
            if 'ACK' in list(value.keys()):
                await self.ACK.write(value['ACK'])
            if 'values' in list(value.keys()):
                await self.values.write(value['values'])
            if 'message' in list(value.keys()):
                await self.message.write(value['message'])

    @CMD.putter  #A Putter for the PV with name CMD
    async def CMD(self, instance, value):
        print('CMD putter received update for the {}, sending new value {}'.format('CMD',value))
        await self.system_io_execute(pv_name = 'CMD', value = value)
        return value

    async def system_io_execute(self, pv_name, value):
        """
        wrapper used to submit commands to the system code for execution

        Parameters
        ----------
        pv_name:  (string)
            string name of the PV
        value:
            new value for the PV specified in the pv_name field

        Returns
        -------

        Examples
        --------
        >>> self.system_io_execute(pv_name = 'CMD', value = '[0]')

        """
        from ubcs_auxiliary.threading import new_thread
        print("@system_io_execute: The {} putter was called with value {}. The system connected is {}".format(pv_name,value,self.system))
        if self.system is not None:
            new_thread(self.system.io_execute,pv_name, value)

class ThreadingClient(object):
    period_pv_name = 'MOCK:period'
    start_pv_name = 'MOCK:start'
    status_pv_name = 'MOCK:status'
    Nested_Indices = 'MOCK:Nested_Indices'
    system = None

    def __init__(self, pvs):
        from caproto.threading.client import Context
        ctx = Context()
        self.pvs = {}
        self.sub = {}
        self.token = {}
        for pv in pvs:
            print(f"subscribing to {pv}")
            self.pvs[pv], = ctx.get_pvs(pv)
            self.sub[pv] = self.pvs[pv].subscribe()
        self.token['MOCK:Nested_Indices'] = self.sub['MOCK:Nested_Indices'].add_callback(self.monitor)


    def monitor(self,response):
        info(f'----------Threading Client monitor---------')
        print(f'system monitor received {response}')
        print(f'response data {response.data}')
        print(f'self.system = {self.system}')
        if self.system is not None:
            print(f'if statement')
            value = response.data
            print(f'response data {bytes(response.data)}')
            print(self.system.io_execute('Nested_Indices', response.data))
            new_thread(self.system.io_execute,'Nested_Indices', value)

    def get_period(self):
        raise NotImplementedError

class SyncClient(object):
    period_pv_name = 'MOCK:period'
    start_pv_name = 'MOCK:start'
    status_pv_name = 'MOCK:status'

    def init(self):
        print('init SyncClient')
        from caproto.sync.client import subscribe
        self.sub = {}
        self.token = {}
        self.sub['period_pv'] = subscribe(self.period_pv_name)
        self.sub['start_pv'] = subscribe(self.start_pv_name)
        self.sub['status_pv'] = subscribe(self.status_pv_name)
        self.token['period_pv'] = self.sub['period_pv'].add_callback(self.monitor)
        self.token['start_pv'] = self.sub['start_pv'].add_callback(self.monitor)
        self.token['status_pv'] = self.sub['period_pv'].add_callback(self.monitor)
        self.sub['period_pv'].block()
        self.sub['start_pv'].block()
        self.sub['status_pv'].block()

    def start(self):
        from ubcs_auxiliary.threading import new_thread
        new_thread(self.init)

    def monitor(self,response):
        print(response)

    def get_period(self):
        raise NotImplementedError

if __name__ == '__main__':
    # The Record Name is specified by prefix
    prefix = 'TEST:SERVER.'
    from pdb import pm
    from tempfile import gettempdir
    import logging
    print(gettempdir()+'/{}.log'.format(prefix))
    logging.basicConfig(filename=gettempdir()+'/{}.log'.format(prefix),
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

    server = Server()
