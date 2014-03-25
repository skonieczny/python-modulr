import unittest
from mock import sentinel, Mock
from modulr.injections import Injector, get_injections, InjectorError


class GetInjectionsTest(unittest.TestCase):
    
    def _test(self, fun, expected_output):
        assertItemsEqual = getattr(self, 'assertItemsEqual', None) or getattr(self, 'assertCountEqual')
        assertItemsEqual(get_injections(fun), expected_output)

    def test_empty(self):
        self._test(lambda: None, [])
        
    def test_one_param(self):
        self._test(lambda x: None, ['x'])
        
    def test_two_params(self):
        self._test(lambda x, y: None, ['x', 'y'])
        
    def test_default_values(self):
        self._test(lambda x, y=5: None, ['x', 'y'])

    def test_args(self):
        self._test(lambda x, y=5, *args: None, ['x', 'y'])

    def test_kwargs(self):
        self._test(lambda x, y=5, **kwargs: None, ['x', 'y'])


class InjectorTests(unittest.TestCase):
    
    def _test(self, fun, injector, expected_params):
        ret = injector.call(fun)
        self.assertEqual(ret, expected_params)
    
    def test_empty(self):
        self._test(lambda: sentinel.output, Injector(), sentinel.output)

    def test_one_param(self):
        self._test(lambda x: [sentinel.output, x], Injector(data={'x': sentinel.x}), [sentinel.output, sentinel.x])

    def test_two_params(self):
        self._test(lambda x, y: [sentinel.output, x, y], Injector(data={'x': sentinel.x, 'y': sentinel.y}), [sentinel.output, sentinel.x, sentinel.y])

    def test_missing(self):
        injector = Injector(data={'x': sentinel.x})
        with self.assertRaises(InjectorError):
            injector.call(lambda x, y: None)
