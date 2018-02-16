# Proof of concept in preparation for APS tomography pipeline trial

## Goals

1. Save valid, standard documents (Event, Resource, Datum, etc.) into databroker
   so that data can be accessed in the future using standard tools.
2. Make the data accessible to an analysis pipeline on a remote machine. Assume
   that the remote machine can mount the filesystem where the detector writes
   its files. Do not assume that the remote machine can access the databroker's
   databases.

## Implementation

1. The ophyd object representing the detector writes Resource and Datum
   documents to a databroker asset Registry in the standard way.
2. The RunEngine emits documents in the standard way.
3. A bluesky 0MQ Publisher, subscribed the RunEngine, publishes documents to a
   0MQ proxy.
4. A bluesky 0MQ RemoteDispatcher, subscribed to this proxy, is forward each
   document in real time. It in turns dispatches the document to one or more
   consumers that do analysis.

Where and why we cheat a little:

Currently, the Datum and Resoruce documents, which contain the filepath and
other information for external data, do not flow through the RunEngine.
Somewhat awkwardly, they are inserted into the database directly by ophyd. This
means that the Publisher and RemoteDispatcher never see them, and they would
need to query the database to get the filepath to open the file. Not ideal!

In the near future (weeks away), the Datum and Resource documents *will* flow
through the RunEngine, and this workflow will become easier to support. Ophyd
will no longer interact with a database directly. Everything will go through the
RunEngine.

In order to support this use case *now* without having to change very much in
the future, we have cheated in the following way:

* We implemented a ``CustomPublisher`` and a ``CustomRemoteDispatcher``.
* Before the Publisher publishes Event documents, it identifies any
  externally-stored data and replaces the datum_id with the actual filepath.
* When the ``CustomRemtoeDispatcher`` receives Event documents, it loads the
  data directly from the file, using some hard-coded knowledge about file
  location, format, and layout.

In the future, we can use a standard Publisher and RemoteDispatcher along with
databroker Handlers. Importantly, all of the "cheating" here is isolated to the
serialized data during communication. All of the long-lived data is standard
and will be accessing using both current and future standard databroker tools.

## Usage

Start three IPython sessions:

1. Start proxy:

    ```
    from bluesky.callbacks.zmq import Proxy
    proxy = Proxy(5567, 5568)
    proxy.start()  # blocks forever
    ```

2. Listen for new documents and analyze them as they come in.

    ```
    %run analyze.py
    dispatcher.start()  # blocks forever
    ```

3. Take data interactively. Documents will be saved to the databroker for access
   later *and* published via 0MQ for immediate analysis.

    ```
    %run collect.py
    RE(count([det]))
    ```

    Each time you execute ``RE(count([det]))`` you should see this line printed
    under ``dispathcer.start()`` in the second window:

    ```
    sum of image data is 25.0
    ```
