PROXIED_OBJECT = '__proxied_object'


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class InstanceProxy(object):

    def __init__(self, proxied_obj):
        self._self = proxied_obj

    @property
    def _self(self):
        try:
            return object.__getattribute__(self, PROXIED_OBJECT)
        except AttributeError:
            return None

    @_self.setter
    def _self(self, proxied_obj):
        object.__setattr__(self, PROXIED_OBJECT, proxied_obj)
        return self

    def __getattribute__(self, attr):
        super_cls_dict = InstanceProxy.__dict__
        cls_dict = object.__getattribute__(self, '__class__').__dict__
        inst_dict = object.__getattribute__(self, '__dict__')
        if attr in cls_dict or attr in inst_dict or attr in super_cls_dict:
            return object.__getattribute__(self, attr)
        target_obj = object.__getattribute__(self, PROXIED_OBJECT)
        return object.__getattribute__(target_obj, attr)

    def __repr__(self):
        class_name =  object.__getattribute__(self, '__class__').__name__
        target_repr = repr(self._self)
        return '<%s( %s )>' % (class_name, target_repr)
