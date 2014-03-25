from modulr.libs.topsort import topsort, CycleError
from modulr.injections import Injector, get_injections


class ComponentContext(object):
    
    def __init__(self, name, config):
        self.name = name
        self.config = config


class Application(object):
    
    def __init__(self, config, component_factory_registry):
        self._config = config
        self._component_factory_registry = component_factory_registry
        self._components = {}

    def _create_injector(self):
        return Injector()

    def _create_component_context(self, configured_component_factory):
        return ComponentContext(configured_component_factory.get_name(), configured_component_factory.get_config())

    def start(self):
        injector = self._create_injector()
        components = []
        for configured_component_factory in self._component_factory_registry.iterate_in_order():
            name = configured_component_factory.get_name()
            context = self._create_component_context(configured_component_factory)
            child_injector = injector.child(context=context)
            component = configured_component_factory.create(self._component_factory_registry, child_injector, self._components)
            self._components[name] = component
            components.append((name, component))
        for name, component in reversed(components):
            # TODO: test it!
            component.init()


class Component(object):
    
    def init(self):
        pass


class ComponentFactoryRegistry(object):
    
    def __init__(self):
        # name => configured factory
        self._factories = {} 
        # interface that implements => name list
        self._factories_by_implements = {}
        
    def load_from_config(self, dict_of_dicts):
        """ dict_of_dicts is: component_name => conponent_config """
        raise NotImplementedError()

    def register(self, configured_factory):
        self._factories[configured_factory.get_name()] = configured_factory
        for interface in configured_factory.get_constraints().get_implements():
            self._factories_by_implements.setdefault(interface, []).append(configured_factory.get_name())
        
    def get_by_name(self, name):
        return self._factories[name]

    def get_by_implements(self, interface):
        return self._factories_by_implements.get(interface, [])

    def iterate_in_order(self):
        dependencies = {}
        for name, configured_factory in self._factories.items():
            dependencies[name] = configured_factory.get_injections(self).values()
        for name in sort_dependencies(dependencies):
            yield self._factories[name]


class ComponentFactory(object):
    
    def __init__(self, fun, constraints):
        self._fun = fun
        self._constraints = constraints
    
    def create(self, injector):
        return injector.call(self._fun)
    
    def get_constraints(self, config):
        """ Notice: `config` param is not used, but passing it allows you to implement different ComponentFactory that uses confing to calculate constraints """
        return self._constraints


class Constraints(object):
    
    def __init__(self, implements, requires):
        self._implements = implements
        self._requires = requires

    def get_implements(self):
        return self._implements
    
    def get_requires(self):
        return self._requires


class ConfiguredComponentFactory(object):
    
    def __init__(self, name, component_factory, config, requirements_mapping=None):
        self._name = name
        self._component_factory = component_factory
        self._config = config
        self._requirements_mapping = {} if requirements_mapping is None else requirements_mapping
        self._constraints = self._component_factory.get_constraints(self._config)

    def get_name(self):
        return self._name
    
    def get_config(self):
        return self._config

    def get_constraints(self):
        return self._constraints
    
    def get_injections(self, component_factory_registry):
        ret = {}
        for require in self._constraints.get_requires():
            candidates = component_factory_registry.get_by_implements(require)
            chosen_candidate = self._requirements_mapping.get(require)
            if not chosen_candidate:
                if len(candidates) == 1:
                    required_component = candidates[0]
                else:
                    if len(candidates) <= 0:
                        raise WrongConfigurationError('Component {} requires {}, but no component implements it. '.format(self._name, require))
                    else:
                        raise WrongConfigurationError('Component {} requires {}, but too many components implements it: {}. Choose one. '.format(self._name, require, ', '.join(candidates)))
            else:
                if chosen_candidate in candidates:
                    required_component = chosen_candidate
                else:
                    raise WrongConfigurationError('Component {} requires {}, but choosen components {} does not implement it. '.format(self._name, require, chosen_candidate))                 
            ret[require] = required_component
        return ret

    def create(self, crf, injector, components_mapping):
        requires = self._constraints.get_requires()
        for require in requires:
            candidates = crf.get_by_implements(require)
            chosen_candidate = self._requirements_mapping.get(require)
            if not chosen_candidate:
                if len(candidates) == 1:
                    required_component = candidates[0]
                else:
                    if len(candidates) <= 0:
                        raise WrongConfigurationError('Component {} requires {}, but no component implements it. '.format(self._name, require))
                    else:
                        raise WrongConfigurationError('Component {} requires {}, but too many components implements it: {}. Choose one. '.format(self._name, require, ', '.join(candidates)))
            else:
                if chosen_candidate in candidates:
                    required_component = chosen_candidate
                else:
                    raise WrongConfigurationError('Component {} requires {}, but choosen components {} does not implement it. '.format(self._name, require, chosen_candidate))                 
            injector.register(require, components_mapping[required_component])
        return self._component_factory.create(injector)


def get_requires_from_injections(component_function):
    injections = get_injections(component_function)
    injections.discard('context')
    return injections


def simple_component_factory(component_function, implements):
    constraints = Constraints(implements, get_requires_from_injections(component_function))
    return ComponentFactory(component_function, constraints)


def sort_dependencies(dependencies):
    pair_list = []
    with_dependencies = set()
    for name, dependants in dependencies.items():
        for dependant in dependants:
            if not dependant in dependencies:
                raise WrongConfigurationError('No such component "{}" needed by "{}". '.format(dependant, name))
            pair_list.append((name, dependant))
            with_dependencies.add(name)
            with_dependencies.add(dependant)
    try:
        ret = topsort(pair_list)
    except CycleError:
        raise WrongConfigurationError('Cycled dependencies. ')
    for name, dependants in dependencies.items():
        if not name in with_dependencies:
            ret.append(name)
    return reversed(ret)


class WrongConfigurationError(Exception):
    pass
