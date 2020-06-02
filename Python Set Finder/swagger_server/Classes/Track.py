import typing
from .Set import Set

Track = typing.NamedTuple('Track', [('artist_name', str), ('song_name', str), ('set_details', Set)])