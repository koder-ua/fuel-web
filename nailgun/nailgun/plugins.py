from multithreading import RLock
from contextlib import contextmanager

from stevedore.hook import HookManager
from stevedore.driver import DriverManager


objs_cache = {}
objs_cache_l = RLock()


def driver(interface, name, *dt, **mp):
    key = (interface, name)
    
    with objs_cache_l:
        if key in objs_cache:
            return objs_cache[key]

    pcls = DriverManager(interface.namespace, name)

    with objs_cache_l:
        if key in objs_cache:
            return objs_cache[key]
        else:
            obj = pcls(*dt, **mp)
            objs_cache[key] = obj

    return obj


def hooks(interface, *dt, **mp):
    key = interface
    
    with objs_cache_l:
        if key in objs_cache:
            return objs_cache[key]

    name = interface.namespace.rsplit('.', 1)[1]
    clss = HookManager(interface.namespace, name)[name]
    objs = []

    with objs_cache_l:
        if key in objs_cache:
            return objs_cache[key]

        for pcls in clss:
            objs.append(pcls(*dt, **mp))
            objs_cache[key] = objs

    return objs
