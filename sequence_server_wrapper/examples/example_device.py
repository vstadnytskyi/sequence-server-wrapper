#!/usr/bin/env python3
from logging import debug, info, warning, error
from time import sleep

import traceback

class DeviceExample():
    def __init__(self):
        self.io = None

    def init(self):
        from time import sleep
        """
        orderly initialization
        """
        debug('Conducting orderly initialization of the Example Device')
        sleep(1)

    def parse_CMD(self,cmd):
        def linear(start=0,end=10,step=1):
            from numpy import arange
            return list(arange(start,end,step))
        try:
            lst = eval(cmd)
        except:
            lst = None
        if type(lst) is list:
            return {'flag':True, 'values':lst}
        else:
            return {'flag':False, 'values':[]}

    def set_VAL(self,value):
        self._VAL = value
        sleep(0.5)
    def get_VAL(self):
        return self._VAL
    VAL = property(get_VAL,set_VAL)

    def io_execute(self,pv_name, value):
        """

        """
        from time import sleep
        print(f'io_execute received: {pv_name},{value}')
        response = ''
        if pv_name == 'CMD':
            self.io_put(pv_name = 'ACK',value = 0)
            self.io_put(pv_name = 'values',value = [])

            reply = self.parse_CMD(value)
            response = ""+str(int(reply['flag']))
            self.trajectory = reply['values']
            if reply['flag'] == False:
                response += f"{'failed to eval the command'}"
            self.io_put(pv_name = 'values',value = reply['values'])
            sleep(1)
            self.io_put(pv_name = 'ACK',value = response)
        if pv_name == 'Nested_Indices':
            print(f'io_execute inside if pv_name == Nested_Indices: {"Nested_Indices"}')
            print(bytes(value))
            index = eval(bytes(value))['test.server']
            self.io_put(pv_name = 'ACK',value = 0)
            try:
                self.VAL = self.trajectory[index]
                flag = True
                resp = ' '
            except:
                resp = traceback.format_exc()
                print(resp)
                flag = False
            print(self.VAL)
            response += resp
            self.io_put(pv_name = 'VAL',value = self.VAL)
            self.io_put(pv_name = 'message',value = response)
            self.io_put(pv_name = 'ACK',value = 1)


            print('response:',reply,response)

    def io_put(self,pv_name, value):
        print(f'DeviceExample.io_put: {pv_name},{value}')
        if self.io is not None:
            if pv_name == 'VAL':
                self.io.io_put_queue.put({pv_name: value})
            else:
                self.io.seq.io_put_queue.put({pv_name: value})



if __name__ is '__main__':
    device = DeviceExample()
    device.init()
