#!/usr/bin/env python3

from caproto.threading.client import Context
prefix = 'MOCK:'
ctx = Context()
start, = ctx.get_pvs(prefix+'start')
status, = ctx.get_pvs(prefix+'status')
period, = ctx.get_pvs(prefix+'period')
Nested_Indices, = ctx.get_pvs(prefix+'Nested_Indices')

if __name__ == '__main__':
    prefix = 'TEST:CLIENT.'
    from pdb import pm
    from tempfile import gettempdir
    import logging
    print(gettempdir()+'/{}.log'.format(prefix))
    logging.basicConfig(filename=gettempdir()+'/{}.log'.format(prefix),
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
