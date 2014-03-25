
import inspect


_sentinel = object()


class Injector(object):
    
    def __init__(self, parent=None, data=None):
        self._parent = parent
        self._data = {} if not data else dict(data)

    def register(self, interface, implementation):
        if interface in self._data:
            raise InjectorError('Interface "{}" allready registered'.format(interface))
        self._data[interface] = implementation
        
    def register_all(self, **kwargs):
        for interface, implementation in kwargs.items():
            self.register(interface, implementation)

    def get(self, interface):
        ret = self._data.get(interface, _sentinel)
        if ret is _sentinel:
            if self._parent:
                return self._parent.get(interface)
            else:
                raise InjectorError('Interface "{}" not found'.format(interface))
        return ret

    def call(self, f, **kwargs):
        injections = dict(kwargs)
        argspec = inspect.getargspec(f)
        for argname in argspec[0]:
            if argname not in kwargs:
                injections[argname] = self.get(argname)
        return f(**injections)

    def child(self, **kwargs):
        ret = Injector(self)
        ret.register_all(**kwargs)
        return ret


def get_injections(fun):
    return set(inspect.getargspec(fun)[0])


class InjectorError(Exception):
    pass
