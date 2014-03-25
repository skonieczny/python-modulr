

_sentinel = object()

class SimilarTo(object):

    def __init__(self, **kwargs):
        self._attrs = kwargs
    
    def __eq__(self, obj):
        for attr_name, attr_value in self._attrs.items():
            if attr_value != getattr(obj, attr_name, _sentinel):
                return False
        return True
