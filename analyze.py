from bluesky.callbacks.zmq import RemoteDispatcher
from bluesky.callbacks import CallbackBase
import h5py
import numpy


class AnalysisPipeline(CallbackBase):
    def start(self, doc):
        ...

    def descriptor(self, doc):
        ...

    def event(self, doc):
        # hack corresponding to the CustomPublisher's hack
        doc['data'] = doc['data'].copy()
        for key in doc['filled']:
            filename = doc['data'][key]
            # TODO Might need a sleep here if the data take some time to 
            # to be visible/accessible on the network.
            with h5py.File(filename) as f:
                arr = f['SOME_KEY_HERE'][:]                
            doc['data'][key] = arr

        # Do analysis on doc now and stash the result on disk or print it.
        print('sum of image data is', numpy.sum(doc['data']['det_image']))


dispatcher = RemoteDispatcher('localhost:5568')
dispatcher.subscribe(AnalysisPipeline())
