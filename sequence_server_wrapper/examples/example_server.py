#!/usr/bin/env python3
from sequence_server_wrapper.template import Server, ThreadingClient
from example_device import DeviceExample

from caproto.server import pvproperty, PVGroup, SubGroup, ioc_arg_parser, run
from caproto import config_caproto_logging
config_caproto_logging()

from logging import debug, info, warning, error

from time import sleep

class ServerExample(PVGroup):
    io_put_queue = None
    io_get_queue = None
    device = None

    io_get_queue = None
    io_put_queue = None

    # Creates the SubGroup for this IO with 'seq.' as subgroup name. The PV banes become: TEST:SERVER.seq.CMD (and ACK, values).
    seq = SubGroup(Server, prefix='seq.')

    # Define PVs for this specific server
    example_pv = pvproperty(value=0.0)
    VAL = pvproperty(value=0.0)

    # run this function when examnple_pv is initilized
    @example_pv.startup
    async def example_pv(self, instance, async_lib):
        debug('* request method called at server startup @example_pv.startup')
        self.io_get_queue = async_lib.ThreadsafeQueue()
        self.io_put_queue = async_lib.ThreadsafeQueue()
        while True:
            print(self.io_put_queue)
            if self.io_put_queue is not None:
                value = await self.io_put_queue.async_get()
                print(f'Got put request from the system main: {value}')
                if 'example_pv' in list(value.keys()):
                    await self.example_pv.write(value['example_pv'])
                if 'VAL' in list(value.keys()):
                    await self.VAL.write(value['VAL'])
            else:
                await async_lib.library.sleep(1)
    # run this function when someone writes in example_pv.
    @example_pv.putter
    async def example_pv(self, instance, value):
        print(f"PV: {'example_pv'} Got 'put' request from outside: new value is {value}")
    # run this function when someone reads from example_pv.
    @example_pv.getter
    async def example_pv(self, instance):
        print(f"PV: {'example_pv'} Got 'get' request from outside")


    @VAL.putter  #A Putter for the PV with name CMD
    async def VAL(self, instance, value):
        print('VAL putter received update for the {}, sending new value {}'.format('VAL',value))
        print(f'self.system = {self.system}')
        await self.system_io_execute(pv_name = 'VAL', value = value)
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

def start(server_prefix, client_pvs):
    from sequence_server_wrapper.template import Server
    from sequence_server_wrapper.template import ThreadingClient
    ioc_options, run_options = ioc_arg_parser(
        default_prefix=server_prefix,
        desc='description')

    io_server  = ServerExample(**ioc_options)

    print(f'io device is {io_server.device}')

    # instantiate of the Device object and initializes it.
    system = DeviceExample()
    system.init()

    # Esteblish crosslinks between device and io (server)
    system.io = io_server
    io_server.seq.system = io_server.system = system

    pvs = client_pvs
    io_client = ThreadingClient(pvs)
    io_client.system = system

    #start async caproto server IO
    run(io_server.pvdb, **run_options)


if __name__ == '__main__':
    client_pvs = ['MOCK:period','MOCK:start','MOCK:status','MOCK:Nested_Indices']
    server_prefix = 'TEST:SERVER.'
    start(server_prefix = 'TEST:SERVER.', client_pvs = client_pvs)
