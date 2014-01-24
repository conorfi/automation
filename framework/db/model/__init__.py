"""
Base model functionality.
"""
from sqlalchemy.sql import table, column


class BaseModel(object):
    """
    Base model class for all models. Offers some common useful functionality.
    """
    def __init__(self, alias=None, db_ignore=None):
        """
        Sets alias and attributes that don't exist in the database
        """
        self._alias = alias or {}
        self._db_ignore = db_ignore or []

    def to_db_field(self, attribute):
        """
        Name of the DB field from obj field
        """
        return self._alias.get(attribute, attribute)

    def to_db_data(self):
        """
        Returns a dict of the model variables to be inserted into the db.

        This will look at all variables in the instance that have a value and
        are not private (by convention) and not in the db ignore list.
        """
        data = dict([(self.to_db_field(k), v)
                     for k, v in vars(self).items()
                     if not k.startswith('_')
                     and k not in self._db_ignore
                     and v is not None])
        return data

    def to_request_data(self):
        """
        Returns a dict of the model variables to make request.
        """
        return self._to_data()

    def to_response_data(self):
        """
        Returns a dict of the model variables expected on response.
        """
        return self._to_data()

    def _to_data(self):
        data = dict([(self._alias.get(k, k), v)
                     for k, v in vars(self).items()
                     if not k.startswith('_')])
        return data


class ModelCrud(object):
    """
    Model Crud operations
    """
    def __init__(self,
                 db=None,
                 tablify=None,
                 klass=None,
                 id=None, unique_key=None):

        if db is None or klass is None or tablify is None \
           or id is None or unique_key is None:
            raise ValueError('All arguments are required')

        super(ModelCrud, self).__init__()
        self.db = db
        self.klass = klass
        self.table = tablify.get_table(klass)
        self.id = id
        self.unique_key = unique_key
        self.instance_cache = {}

    def cache_add(self, instance):
        key = getattr(instance, self.id)
        self.instance_cache[key] = instance

    def cache_remove(self, instance):
        key = getattr(instance, self.id)
        if key in self.instance_cache:
            del self.instance_cache[key]

    def clear_cache(self):
        """
        Clears the DB cache for this model
        """
        cache = self.instance_cache.copy()
        for key, instance in cache.iteritems():
            self.delete(instance)

    def check_instance(self, instance):
        """
        Checks if the instance belongs to this model
        """
        if not isinstance(instance, self.klass):
            raise ValueError('Instance is not of expected class.')

    def create(self, model_instance):
        """
        Create a new model in the user table, returns updated model with new DB
        ID.

        :param model_instance:
        """
        self.check_instance(model_instance)

        model_data = model_instance.to_db_data()
        table_field = model_instance.to_db_field(self.id)

        query = self.table.insert().values(**model_data). \
            returning(getattr(self.table.c, table_field, None))

        result = self.db.execute(query)
        setattr(model_instance, self.id, result[0][table_field])
        self.cache_add(model_instance)
        return model_instance

    def _table_op(self, op_func, model_instance):
        """
        Does table operation against the unique key

        :param op_func:
        :param model_instance:
        """

        self.check_instance(model_instance)

        value = getattr(model_instance, self.unique_key, None)
        if value:
            table_field = model_instance.to_db_field(self.unique_key)
            query = op_func().\
                where(getattr(self.table.c, table_field, None) == value)

            return self.db.execute(query)

    def delete(self, model_instance):
        """
        Deletes the given instance.

        :param model_instance:
        """
        result = self._table_op(self.table.delete, model_instance)
        self.cache_remove(model_instance)
        return result

    def read(self, model_instance):
        """
        Returns the instance from the DB for this model.

        :param group:
        """
        data = self._table_op(self.table.select, model_instance)
        db_obj = self.klass(**data[0]) if len(data) > 0 else None
        return db_obj


class Tablify(object):
    """
    Model to table utility
    """
    def is_model_attribute(self, instance, attr):
        """
        Predicate to determine if the attribute is in the db model
        :param attr:
        """
        return \
            attr is not None \
            and not attr.startswith('_') \
            and not attr.isupper() \
            and attr not in instance._db_ignore

    def get_table(self, klass):
        """
        Get sql alchemy table for a class that doesn't require params
        """
        instance = klass()
        columns = [column(instance._alias.get(attr, attr))
                   for attr in vars(instance).keys()
                   if self.is_model_attribute(instance, attr)]
        return table(klass.TABLE_NAME, *columns)
