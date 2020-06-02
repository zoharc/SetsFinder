from .Set import Set
import typing

SetAndOccurences = typing.NamedTuple('SetAndOccurences', [('set_data', Set), ('occurences', int)])
