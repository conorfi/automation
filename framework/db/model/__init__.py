"""
Base model functionality.
"""


class BaseModel(object):
    """
    Base model class for all models. Offers some common useful functionality.
    """

    def to_data(self, exclude_empty=False):
        """
        Returns a dict of the model variables

        :param exclude_empty: exclude empty vars from data?
        """
        data = vars(self).copy()
        if exclude_empty:
            data = dict(
                filter(lambda value: value[1] is not None, data.items())
            )
        return data
