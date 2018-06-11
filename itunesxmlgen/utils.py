from lxml import etree as et
from random import randint
import uuid


def strand(length=None):
    """ Returns random string with len = `length`
    """
    return uuid.uuid4().hex[:length]


def intrand(minimum=0, maximum=1000000):
    """ Returns random int between `minimum` and `maximum` (0 - 1000000 by default)
    """
    return randint(a=minimum, b=maximum)


class Sequence:
    def __init__(self, start=1):
        self.__gen = sequence(start=start)
        self.__current = start

    @property
    def current(self):
        return self.__current

    @property
    def next(self):
        self.__current = next(self.__gen)
        return self.current


def sequence(start=1):
    idx = start
    while True:
        yield idx
        idx += 1


def tostring(node, decode=True, encoding='UTF-8'):
    _bytes = et.tostring(
        element_or_tree=node,
        encoding=encoding,
        xml_declaration=True,
        pretty_print=True
    )
    return _bytes if not decode else _bytes.decode(encoding)


def validate_less(small, big, small_name, big_name):
    """ Check that `big` is not less than `small`, raise ValueError otherwise

    :param small: smaller value to check
    :param big: bigger value to check
    :param small_name: smallest param name for format error
    :param big_name: bigger param name for format error

    :raise ValueError
    """
    err = __validate_less(small, big, small_name, big_name)
    if err:
        raise ValueError(err)


def __validate_less(small, big, small_name, big_name):
    if small > big:
        return (
            '{small_name} ({small}) must be less than {big_name} ({big})'
        ).format(
            small=small, small_name=small_name, big=big, big_name=big_name
        )


def validate_positive(value, value_name, strict=True):
    """ Check that `value` is positive

    :param value: value to check
    :param value_name: value param name for format error
    :param strict: is zero value not correct?

    :raise ValueError
    """
    err = __validate_positive(value, value_name, strict)
    if err:
        raise ValueError(err)


def __validate_positive(value, value_name, strict=True):
    if value < 0 or (value == 0 and strict):
        return '{value_name} ({value}) must be positive'.format(
            value_name=value_name, value=value
        )
