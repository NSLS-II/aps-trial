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

3. Take data interactively. Documents will be published.

    ```
    %run collect.py
    RE(count([det]))
    ```

    Each you execute ``RE(count([det]))`` you should see this line printed under
    ``dispathcer.start()`` in the second window:

    ```
    sum of image data is 25.0
    ```
