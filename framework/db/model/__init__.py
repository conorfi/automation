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

    def to_db_data(self):
        """
        Returns a dict of the model variables to be inserted into the db.

        This will look at all variables in the instance that have a value and
        are not private (by convention) and not in the db ignore list.
        """
        data = dict([(self._alias.get(k, k), v)
                     for k, v in vars(self).items()
                     if not k.startswith('_')
                     and k not in self._db_ignore
                     and v is not None])
        return data

    def to_request_data(self):
        """
        Returns a dict of the model variables to make request.
        """
        data = dict([(self._alias.get(k, k), v)
                     for k, v in vars(self).items()
                     if not k.startswith('_')])
        return data

    def to_response_data(self):
        """
        Returns a dict of the model variables expected on response.
        """
        # expecting to match request format by default
        return self.to_request_data()


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
