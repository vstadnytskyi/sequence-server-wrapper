#!/usr/bin/env python3

from caproto.sync.client import read, write
prefix = 'TEST:SERVER.'

PV_list = ['seq.CMD',
            'seq.ACK',
            'seq.values',
            'example_pv']

if __name__ == '__main__':
    prefix = 'TEST:CLIENT.'
    from pdb import pm
    from tempfile import gettempdir
    import logging
    print(gettempdir()+'/{}.log'.format(prefix))
    logging.basicConfig(filename=gettempdir()+'/{}.log'.format(prefix),
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
