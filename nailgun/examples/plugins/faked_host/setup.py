from setuptools import setup, find_packages
from nailgun.plugin_interface import INGBackgroundTask, def_plug_name

name = def_plug_name(INGBackgroundTask)
setup(
    name='faked_host',
    version='1.0',
    packages=find_packages(),
    entry_points={
        INGBackgroundTask.namespace: [
            name + ' = faked_host:FakedHost',
        ],
    },
    zip_safe=False,
)
