#!/usr/bin/env python3

from caproto.threading.client import Context
prefix = 'TEST:SERVER.'
ctx = Context()
CMD, = ctx.get_pvs(prefix+'seq.CMD')
ACK, = ctx.get_pvs(prefix+'seq.ACK')
message, = ctx.get_pvs(prefix+'seq.message')
values, = ctx.get_pvs(prefix+'seq.values')
example_pv, = ctx.get_pvs(prefix+'example_pv')
VAL, = ctx.get_pvs(prefix+'VAL')

if __name__ == '__main__':
    prefix = 'TEST:CLIENT.'
    from pdb import pm
    from tempfile import gettempdir
    import logging
    print(gettempdir()+'/{}.log'.format(prefix))
    logging.basicConfig(filename=gettempdir()+'/{}.log'.format(prefix),
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
