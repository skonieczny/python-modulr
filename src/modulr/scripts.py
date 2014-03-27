

class ScriptsManager(object):
    
    def __init__(self):
        self._registry = {}
        
    def register(self, script_name, handler):
        if script_name in self._registry:
            raise ValueError('Script {} allready registered. '.format(script_name))
        self._registry[script_name] = handler
    
    def run_script(self, script_name, args):
        if not script_name in self._registry:
            raise ValueError('Unknown script: {}.'.format(script_name))
        return self._registry[script_name](args)
        
    def run_script_from_argv(self, argv):
        script_name = argv[1]
        args = argv[2:]
        return self.run_script(script_name, args)
