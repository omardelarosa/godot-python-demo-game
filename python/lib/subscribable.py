NOOP = lambda x: x


class Subscribable:
    def __init__(self):
        self._callbacks = {}

    def subscribe(self, dictionary_of_callback_bindings: dict):
        for k, v in dictionary_of_callback_bindings.items():
            if k not in self._callbacks:
                self._callbacks[k] = []
            if isinstance(v, list):
                for h in v:
                    self._callbacks[k].append(h)
            else:
                self._callbacks[k].append(v)

    def unsubscribe(self, dictionary_of_callback_bindings: dict):
        for k, v in dictionary_of_callback_bindings.items():
            if k in self._callbacks:
                if isinstance(v, list):
                    for h in v:
                        if h in self._callbacks[k]:
                            self._callbacks[k].remove(h)
                else:
                    self._callbacks[k].remove(v)

    def send(self, event_signal_key, *args):
        # Call
        if event_signal_key in self._callbacks:
            for callback in self._callbacks[event_signal_key]:
                callback(*args)

    def emit(self, signal_key, *args):
        # To be implemented by subclasses
        return