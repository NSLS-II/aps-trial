from bluesky.callbacks.zmq import RemoteDispatcher
from bluesky.callbacks import CallbackBase
import h5py
import numpy

import pickle
import asyncio
from bluesky.run_engine import DocumentNames

class CustomRemoteDispatcher(RemoteDispatcher):
    @asyncio.coroutine
    def _poll(self):
        while True:
            message = yield from self._socket.recv()
            hostname, pid, RE_id, name, doc = message.split(b' ', 4)
            hostname = hostname.decode()
            pid = int(pid)
            RE_id = int(RE_id)
            name = name.decode()
            if self._is_our_message(hostname, pid, RE_id):
                doc = pickle.loads(doc)
                # CUSTOM CODE
                if name == 'event':
                    doc = decode_hack(doc)
                # END CUSTOM CODE
                self.loop.call_soon(self.process, DocumentNames[name], doc)


def decode_hack(doc):
    # hack corresponding to the CustomPublisher's hack
    doc['data'] = doc['data'].copy()
    for key in doc['filled']:
        filename = doc['data'][key]
        # TODO Might need a sleep here if the data take some time to 
        # to be visible/accessible on the network.
        with h5py.File(filename) as f:
            arr = f['SOME_KEY_HERE'][:]                
        doc['data'][key] = arr
    return doc


class AnalysisPipeline(CallbackBase):
    def start(self, doc):
        ...

    def descriptor(self, doc):
        ...

    def event(self, doc):
        # Do analysis on doc now and stash the result on disk or print it.
        print('sum of image data is', numpy.sum(doc['data']['det_image']))


dispatcher = CustomRemoteDispatcher('localhost:5568')
dispatcher.subscribe(AnalysisPipeline())
