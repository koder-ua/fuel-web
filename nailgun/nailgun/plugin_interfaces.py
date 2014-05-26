import abc


def def_plug_name(interface):
    return interface.namespace.split('.')[-1]


class INGBackgroundTask(object):
    __metaclass__ = abc.ABCMeta
    namespace = 'nailgun.bgtask'

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

