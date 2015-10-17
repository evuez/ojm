# -*- coding: utf-8 -*-

import json
from time import strftime
from os import path, remove
from glob import glob
from uuid import uuid4


STORAGE = 'ojm.data'


class ModelNotFound(Exception):
    pass


_models = {}
def register(model):
    """
    Register a class to allow object loading from JSON.
    """
    _models[model.__name__] = model


def storable(obj):
    """
    Remove fields that can't / shouldn't be stored.
    """
    def get_data(a):
        if a.startswith('linked_'):
            return getattr(getattr(obj, a), 'uuid', None)
        else:
            return getattr(obj, a)
    return {
        a:get_data(a) for a in dir(obj)
            if not a.startswith('_')
            and not hasattr(
                getattr(obj, a),
                '__call__'
            )
    }


class Model(object):
    def __init__(self):
        self.uuid = uuid4().hex
        self.created = None
        self.updated = None

    def save(self):
        """
        Save current instance to a JSON file.
        """
        fname = path.join(
            STORAGE,
            '{0}_{1}'.format(
                self.__class__.__name__.lower(),
                self.uuid
            )
        )
        if path.isfile(fname):
            raise IOError("Cannot overwrite existing model!")
        self.created = strftime('%Y-%m-%d %H:%M:%S')
        data = storable(self)
        with open(fname, 'w') as out:
            json.dump(
                obj=data,
                fp=out,
                separators=(',',':'),
                default=storable
            )

    def update(self):
        """
        Update JSON file with current instance.
        """
        fname = path.join(
            STORAGE,
            '{0}_{1}'.format(
                self.__class__.__name__.lower(),
                self.uuid
            )
        )
        if not path.isfile(fname):
            raise IOError("Cannot update unsaved model!")
        self.updated = strftime('%Y-%m-%d %H:%M:%S')
        data = storable(self)
        with open(fname, 'w') as out:
            json.dump(
                obj=data,
                fp=out,
                separators=(',',':'),
                default=storable
            )

    def delete(self):
        """
        Delete saved instance.
        """
        fname = path.join(
            STORAGE,
            '{0}_{1}'.format(
                self.__class__.__name__.lower(),
                self.uuid
            )
        )
        try:
            remove(fname)
        except OSError:
            raise ModelNotFound

    @classmethod
    def load(cls, uuid=None, str_=None):
        """
        Load an object.
        If `uuid` is provided, will try to laod using this uuid.
        `str_` must be a JSON string. If `uuid` isn't provided but `str_` is,
        it will try to load the object using this JSON string.
        """
        if not any((uuid, str_)):
            return None
        if uuid is None:
            data = json.loads(str_)
        else:
            fname = path.join(
                STORAGE,
                '{0}_{1}'.format(
                    cls.__name__.lower(),
                    uuid
                )
            )
            try:
                with open(fname, 'r') as out:
                    data = json.load(out)
            except IOError:
                raise ModelNotFound("Model {0} not found".format(fname))
        obj = cls()
        for attr in storable(obj).keys():
            element = None
            if attr not in data or attr.startswith('_'):
                continue
            if attr.startswith('embedded_') and attr.endswith('s'):
                element = []
                for embedded in data[attr]:
                    element.append(_models[
                        attr[9:-1].title()
                    ].loads(json.dumps(embedded)))
            elif attr.startswith('embedded_'):
                element = _models[
                    attr[9:].title()
                ].loads(json.dumps(data[attr]))
            elif attr.startswith('linked_') and attr.endswith('s'):
                element = []
                for linked in data[attr]:
                    element.append(_models[attr[7:-1].title()].load(linked))
            elif attr.startswith('linked_'):
                element = _models[attr[7:].title()].load(data[attr])
            if element is None:
                element = data[attr]
            if not attr.startswith('_'):
                setattr(obj, attr, element)
        return obj

    @classmethod
    def loads(cls, str_):
        """
        Short for `Model.load(str_=json)`.
        """
        return cls.load(str_=str_)

    @classmethod
    def load_all(cls, start=0, stop=None):
        """
        Load every objects that are instances of the current class.
        `start` and `stop` can be provided to limit output.
        """
        return [
            cls.load(path.basename(f).partition('_')[2])
            for f in glob(path.join(
                STORAGE,
                '{0}_*'.format(cls.__name__.lower())
            ))[start:stop]
        ]

    def duplicate(self):
        """
        When loading an existing object, to create a copy of this object and
        be able to save it, a new UUID must be generated.
        This method simply generate a new UUID.
        """
        self.uuid = uuid4().hex
        return self
