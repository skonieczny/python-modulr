import unittest
from mock import sentinel, Mock
from modulr.scripts import ScriptsManager
from .helpers import SimilarTo


class ScriptsManagerTest(unittest.TestCase):
    
    def test_empty(self):
        sm = ScriptsManager()
        with self.assertRaises(ValueError):
            sm.run_script_from_argv([sentinel.program_name, 'no_such_command'])

    def test_simple_call(self):
        script_name = 'script_name'
        script = Mock(return_value=sentinel.output)
        sm = ScriptsManager()
        sm.register('script_name', script)
        output = sm.run_script_from_argv([sentinel.program_name, 'script_name'])
        self.assertEquals(output, sentinel.output)
        script.assert_called_once_with([])

    def test_arguments(self):
        script_name = 'script_name'
        script = Mock(return_value=sentinel.output)
        sm = ScriptsManager()
        sm.register('script_name', script)
        output = sm.run_script_from_argv([sentinel.program_name, 'script_name', sentinel.arg1, sentinel.arg2])
        self.assertEquals(output, sentinel.output)
        script.assert_called_once_with([sentinel.arg1, sentinel.arg2])
