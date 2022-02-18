import sys
sys.path.append('..')
from ftp_script_server import ftp_download_dir
import logging
import importlib
import inspect
try:
    #python3
    from importlib import reload
except:
    #python2
    pass
def load_package(package_name):
    '''download up-to-date package files and reload all modules'''
    logging.info('downloading project package')
    ftp_download_dir(package_name)
    logging.info('project package downloaded')
    sys.path.append('../' + package_name)
    __import__(package_name)
    main_module = None
    for module in sys.modules.values():
        if module and module.__name__.startswith(package_name + '.'):
            obj = find_main_class(module)
            if obj:
                main_module = module
            try:
                reload(module)
            except:
                pass
    reload(main_module)
    main_class = find_main_class(main_module)
    return main_class

def find_main_class(module):
    '''find the main worker by name'''
    for obj in vars(module).values():
        if inspect.isclass(obj) and getattr(obj, 'name', None):
            return obj
