import unittest
from mock import sentinel, Mock
from modulr.application import ComponentFactoryRegistry, Application, simple_component_factory,\
    WrongConfigurationError, ConfiguredComponentFactory
from .helpers import SimilarTo

_sentinel = object()


class Component(object):
    
    def __init__(self):
        self.inited = 0
    
    def init(self):
        self.inited += 1


class ApplicationTest(unittest.TestCase):
    
    def test_no_components(self):
        cfr = ComponentFactoryRegistry()
        app = Application({}, cfr)
        app.start()

    def test_no_depends_no_injections(self):
        component_calls = []
        component_instance = Component()
        def component():
            component_calls.append(None)
            return component_instance
        factory = simple_component_factory(component, ['component_interface'])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('component_name', factory, sentinel.component_config))
        app = Application({}, cfr)
        app.start()
        self.assertEquals(1, len(component_calls))
        self.assertEquals(1, component_instance.inited)

    def test_no_depends(self):
        component_instance = Component()
        component_calls = []
        def component(context):
            component_calls.append(context)
            return component_instance
        factory = simple_component_factory(component, ['component_interface'])
        
        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('component_name', factory, sentinel.component_config))
        app = Application({}, cfr)
        app.start()
        self.assertListEqual(component_calls, [SimilarTo(config=sentinel.component_config, name='component_name', scripts_manager=app._scripts_manager)])
        self.assertEquals(1, component_instance.inited)

    def test_one_depend(self):
        dependant_component_instance = Component()
        dependant_component_calls = []
        def dependant_component():
            dependant_component_calls.append(None)
            return dependant_component_instance
        dependant_factory = simple_component_factory(dependant_component, ['dependant'])

        depending_component_instance = Component()
        depending_component_calls = []
        def depending_component(dependant):
            depending_component_calls.append(dependant)
            return depending_component_instance
        depending_factory = simple_component_factory(depending_component, ['depending'])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('dependant_component_name', dependant_factory, sentinel.dependant_component_config))
        cfr.register(ConfiguredComponentFactory('depending_component_name', depending_factory, sentinel.depending_component_config))
        app = Application({}, cfr)
        app.start()
        self.assertEquals(1, len(dependant_component_calls))
        self.assertListEqual(depending_component_calls, [dependant_component_instance])
        self.assertEquals(1, dependant_component_instance.inited)
        self.assertEquals(1, depending_component_instance.inited)

    def test_missing_depend(self):
        depending_component_instance = Component()
        depending_component_calls = []
        def depending_component(dependant):
            depending_component_calls.append(dependant)
            return depending_component_instance
        depending_factory = simple_component_factory(depending_component, ['depending'])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('depending_component_name', depending_factory, sentinel.depending_component_config))
        app = Application({}, cfr)
        with self.assertRaises(WrongConfigurationError):
            app.start()

    def test_multiple_implements(self):
        component1_calls = []
        def component1():
            component1_calls.append(None)
            return Component()
        factory1 = simple_component_factory(component1, ['component_interface'])

        component2_calls = []
        def component2():
            component2_calls.append(None)
            return Component()
        factory2 = simple_component_factory(component2, ['component_interface'])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('component1_name', factory1, sentinel.component1_config))
        cfr.register(ConfiguredComponentFactory('component2_name', factory2, sentinel.component2_config))
        app = Application({}, cfr)
        app.start()
        self.assertEquals(1, len(component1_calls))
        self.assertEquals(1, len(component2_calls))

    def test_multiple_implements_no_manual_selection(self):
        component1_calls = []
        def component1():
            component1_calls.append(None)
            return Component()
        factory1 = simple_component_factory(component1, ['component_interface'])

        component2_calls = []
        def component2():
            component2_calls.append(None)
            return Component()
        factory2 = simple_component_factory(component2, ['component_interface'])

        component3_calls = []
        def component3(component_interface):
            component3_calls.append(component_interface)
            return Component()
        factory3 = simple_component_factory(component3, [])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('component1_name', factory1, sentinel.component1_config))
        cfr.register(ConfiguredComponentFactory('component2_name', factory2, sentinel.component2_config))
        cfr.register(ConfiguredComponentFactory('component3_name', factory3, sentinel.component3_config))
        app = Application({}, cfr)
        with self.assertRaises(WrongConfigurationError):
            app.start()

    def test_multiple_implements_and_manual_selection(self):
        component1_calls = []
        def component1():
            component1_calls.append(None)
            return Component()
        factory1 = simple_component_factory(component1, ['component_interface'])

        component2_calls = []
        component2_instance = Component()
        def component2():
            component2_calls.append(None)
            return component2_instance
        factory2 = simple_component_factory(component2, ['component_interface'])

        component3_calls = []
        def component3(component_interface):
            component3_calls.append(component_interface)
            return Component()
        factory3 = simple_component_factory(component3, [])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('component1_name', factory1, sentinel.component1_config))
        cfr.register(ConfiguredComponentFactory('component2_name', factory2, sentinel.component2_config))
        cfr.register(ConfiguredComponentFactory('component3_name', factory3, sentinel.component3_config, {'component_interface': 'component2_name'}))
        app = Application({}, cfr)
        app.start()
        self.assertEquals(1, len(component1_calls))
        self.assertEquals(1, len(component2_calls))
        self.assertEquals([component2_instance], component3_calls)

    def test_multiple_implements_and_manual_selection_but_wrong(self):
        component1_calls = []
        def component1():
            component1_calls.append(None)
            return Component()
        factory1 = simple_component_factory(component1, ['component_interface'])

        component2_calls = []
        component2_instance = Component()
        def component2():
            component2_calls.append(None)
            return component2_instance
        factory2 = simple_component_factory(component2, ['not_component_interface'])

        component3_calls = []
        def component3(component_interface):
            component3_calls.append(component_interface)
            return Component()
        factory3 = simple_component_factory(component3, [])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('component1_name', factory1, sentinel.component1_config))
        cfr.register(ConfiguredComponentFactory('component2_name', factory2, sentinel.component2_config))
        cfr.register(ConfiguredComponentFactory('component3_name', factory3, sentinel.component3_config, {'component_interface': 'component2_name'}))
        app = Application({}, cfr)
        with self.assertRaises(WrongConfigurationError):
            app.start()

    def test_dependencies_cycle(self):
        component1_calls = []
        def component1(component2_interface):
            component1_calls.append(None)
            return Component()
        factory1 = simple_component_factory(component1, ['component1_interface'])

        component2_calls = []
        def component2(component3_interface):
            component2_calls.append(None)
            return Component()
        factory2 = simple_component_factory(component2, ['component2_interface'])

        component3_calls = []
        def component3(component1_interface):
            component3_calls.append(None)
            return Component()
        factory3 = simple_component_factory(component3, ['component3_interface'])

        cfr = ComponentFactoryRegistry()
        cfr.register(ConfiguredComponentFactory('component1_name', factory1, sentinel.component1_config))
        cfr.register(ConfiguredComponentFactory('component2_name', factory2, sentinel.component2_config))
        cfr.register(ConfiguredComponentFactory('component3_name', factory3, sentinel.component3_config))
        app = Application({}, cfr)
        with self.assertRaises(WrongConfigurationError):
            app.start()
