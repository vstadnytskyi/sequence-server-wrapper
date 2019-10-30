#!/usr/bin/env python3

from caproto.server import pvproperty, PVGroup, SubGroup, ioc_arg_parser, run

from logging import debug, info, warning, error

from time import sleep

class MockServer(PVGroup):
    io_put_queue = None

    # Define PVs for this specific server
    start = pvproperty(value=0)
    status = pvproperty(value='stop')
    period = pvproperty(value=0.0)
    Nested_Indices = pvproperty(value="{'test.server':0}")


    # run this function when examnple_pv is initilized
    @start.startup
    async def start(self, instance, async_lib):
        debug('* request method called at server startup @start.startup')
        while True:
            if self.io_put_queue is not None:
                value = await self.io_put_queue.async_get()
                debug(f'Got put request from the device: {value}')
                if 'start' in list(value.keys()):
                    await self.start.write(value['start'])
            else:
                await async_lib.library.sleep(1)
    # run this function when someone writes in start.
    @start.putter
    async def start(self, instance, value):
        debug(f"PV: {'start'} Got 'put' request from outside: new value is {value}")
    # run this function when someone reads from start.
    @start.getter
    async def start(self, instance):
        print(f"PV: {'start'} Got 'get' request from outside")

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='MOCK:',
        desc='description')
    io  = MockServer(**ioc_options)


    #start async caproto server IO
    run(io.pvdb, **run_options)
