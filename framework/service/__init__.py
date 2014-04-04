"""
Common service functionality
"""


class ModelService(object):
    """
    Template of a common set of functions for generating and
    checking model data.
    """

    def __init__(self, klass, dao, defaults):
        """
        Instantiates the template with the given class, DAO and defaults.

        :param klass: model class
        :param dao: DAO for model class
        :param defaults: dict of default values when generating model. Values
        may be static value or callable that returns value.
        """
        self.klass = klass
        self.dao = dao
        self.defaults = defaults

    def generate(self, **kwargs):
        """
        Generates a random object, optionally overriding the defaults with
        given keyword args.

        :param kwargs:
        """
        instance_defaults = {}
        for key, value in self.defaults.iteritems():
            if callable(value):
                instance_value = value()
            else:
                instance_value = value
            instance_defaults[key] = instance_value
        instance_defaults.update(kwargs)
        return self.klass(**instance_defaults)

    def create_random(self, **kwargs):
        """
        Generates a random object in the DB, optionally overriding the defaults
        with given keyword args.

        :param kwargs:
        """
        obj = self.generate(**kwargs)
        self.dao.create(obj)
        return obj

    def remove(self, obj):
        """
        Deletes the given object from the DB, if it exists.

        :param obj:
        """
        self.dao.delete(obj)

    def exists(self, obj):
        """
        Returns True if the object data exists in the DB, False otherwise.

        :param obj:
        """
        db_obj = self.dao.read(obj)
        return db_obj is not None
