========
Overview
========

This library uses EPICS Channel Access protocol for communication between different servers. It provides a simple template that adds additional process variables(PVs) to EPICS records used for data acquisition. It utilizes the subgroup concept developed in Caproto (https://caproto.github.io/caproto/iocs.html#subgroups).

Conceptually the wrapper is very simple. It provides means to channel information from the network (via CA) to the underlying system level code.

The template_server.py has a Server class.

.. code-block:: python
   :emphasize-lines: 4,7,8,9

   from caproto.server import PVGroup
   class Server(PVGroup):
     #placeholder for the self.system attribute
     system = None

     # define relavant PVs.
     CMD = pvproperty(value='This is command string', max_length = 10000, dtype = str)
     ACK = pvproperty(value='0', read_only = True, dtype = str)
     values = pvproperty(value=[nan,nan], read_only = True, max_length = 10000)

     ...


Upon startup of the caproto io server, two async thread safe queue are created

.. code-block:: python

   @CMD.startup #this function will be executed on instantiaton
   async def CMD(self, instance, async_lib):
       print('* request method called at server startup @CMD.startup')
       self.io_get_queue = async_lib.ThreadsafeQueue()
       self.io_put_queue = async_lib.ThreadsafeQueue()


the system level instance if exist gets these queues and uses them to communicate information back to the IO.

.. code-block:: python

  if self.system is not None:
     self.system.io_put_queue = self.io_put_queue
     self.system.io_get_queue = self.io_get_queue


The putter function for CMD PV will submit the new value of the PV to the system code for execution:

.. code-block:: python

  @CMD.putter  #A Putter for the PV with name CMD
  async def CMD(self, instance, value):
      print('CMD putter received update for the {}, sending new value {}'.format('CMD',value))
      await self.system_io_execute(pv_name = 'CMD', value = value)
      return value

where self.system_io_execute act as a wrapper and used to submit commands to the system code for execution.

.. autoclass:: sequence_server_wrapper.template.Server
  :members:

Start by importing Sequence Server Wrapper.

.. code-block:: python

    import sequence_server_wrapper
