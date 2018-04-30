from lxml import etree as et
from random import randint
import uuid


def strand(length=None):
    """ Returns random string with len = <length>
    """
    return uuid.uuid4().hex[:length]


def intrand(minimum=0, maximum=1000000):
    """ Returns random int between <minimum> and <maximum> (0 - 1000000 by default)
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
