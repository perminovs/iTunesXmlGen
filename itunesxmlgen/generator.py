from datetime import datetime
from lxml import etree as et
from random import sample, choice
from .utils import Sequence, strand, intrand, validate_less


__track_id = None
__playlist_id = None


def generate_xml(
    tracks_cnt=10, artists_cnt=5, playlists_cnt=3, playlist_fill_rate=5,
    playlist_fill_variety=0,
):
    """ Returns full iTunes xml

    :param tracks_cnt: count of xml Tracks
    :param artists_cnt: count of Artists, generated for Tracks
    :param playlists_cnt: count of Playlist
    :param playlist_fill_rate: count of Tracks in one Playlist
    :param playlist_fill_variety: variety of `playlist_fill_rate` param

    Count of playlist tracks will be:
    `playlist_fill_rate` +/- `playlist_fill_variety`
    """
    validate_less(
        small=playlist_fill_rate, big=tracks_cnt,
        small_name='Count of Tracks in Playlist', big_name='Count of Tracks'
    )
    validate_less(
        small=playlist_fill_variety, big=playlist_fill_rate,
        small_name='Variety of Playlist filling', big_name='Count of Playlists'
    )

    global __track_id, __playlist_id
    __track_id, __playlist_id = Sequence(), Sequence()

    root = et.Element('plist', attrib={'version': "1.0"})
    data = et.Element('dict')

    fill_xml_head(parent_node=data)

    track_key_node, track_container = xml_tracks(
        tracks_cnt=tracks_cnt, artists_cnt=artists_cnt)
    data.append(track_key_node)
    data.append(track_container)

    plst_key_node, playlist_container = xml_playlists(
        cnt=playlists_cnt, fill_rate=playlist_fill_rate,
        fill_variety=playlist_fill_variety
    )
    data.append(plst_key_node)
    data.append(playlist_container)

    root.append(data)

    return root


def fill_xml_head(parent_node):
    """ Fill general xml attributes
    """
    _add_param = param_add_factory(parent_node=parent_node)
    _add_param('Major Version', 1, type_='integer')
    _add_param('Minor Version', 1, type_='integer')
    _add_param('Application Version', '12.7.3.46')
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    _add_param('Date', now, type_='date')
    _add_param('Features', 5, type_='integer')
    _add_param('Library Persistent ID', strand(10))


def xml_tracks(tracks_cnt, artists_cnt):
    """  Returns `cnt` pair of tags (<track_id>, <track>), represents iTunes tracks
    """
    key_node = compile_node(text='Tracks')

    artist_pool = ['artist_{}'.format(strand(5)) for _ in range(artists_cnt)]

    track_container = et.Element('dict')
    for track_idx in range(tracks_cnt):
        artist_idx = track_idx
        while artist_idx >= len(artist_pool):
            artist_idx -= len(artist_pool)
        artist = artist_pool[artist_idx]

        id_node, track_node = xml_track(
            title='track_'.format(strand(7)),
            artist=artist,
            album='album_'.format(strand(7)),
        )
        track_container.append(id_node)
        track_container.append(track_node)
    return key_node, track_container


def xml_track(**kwargs):  # TODO support more attributes
    """ Returns two tags, represents iTunes track id and track

    Supported kwargs: `title`, `artist`, `album`

    :return tuple(<id_node>, <track_node>)
    """
    track_id = __track_id.next
    id_node = compile_node(text=track_id)

    track_node = et.Element('dict')

    _add_param = param_add_factory(parent_node=track_node)

    _add_param(key='Track ID', value=track_id, type_='integer')
    _add_param(key='Name', value=kwargs.get('title', None))
    _add_param(key='Artist', value=kwargs.get('artist', None))
    _add_param(key='Album', value=kwargs.get('album', None))

    return id_node, track_node


def xml_playlists(cnt, fill_rate, fill_variety):
    """ Retunrs `cnt` pairs of tags (<playlist_id>, <playlist>), represents iTunes playlist
    """
    key_node = compile_node(text='Playlists')
    playlist_container = et.Element('array')
    for _ in range(cnt):
        track_cnt = intrand(
            minimum=fill_rate - fill_variety,
            maximum=fill_rate + fill_variety
        )
        playlist = xml_playlist(
            name='playlist_{}'.format(strand(10)),
            track_cnt=track_cnt,
        )
        playlist_container.append(playlist)
    return key_node, playlist_container


def xml_playlist(name, track_cnt):
    """ Returns xml tag, represents one iTunes playlist

    :param name: playlist name
    :param track_cnt: number of playlist tracks

    :return: <playlist_node>
    """
    playlist_node = et.Element('dict')
    playlist_id = __playlist_id.next

    _add_param = param_add_factory(parent_node=playlist_node)

    _add_param(key='Playlist ID', value=playlist_id, type_='integer')
    _add_param(key='Name', value=name, type_='string')

    items_key = compile_node(text='Playlist Items')

    available_ids = sample(range(1, __track_id.current + 1), track_cnt)
    items_array = et.Element('array')
    for track_id in available_ids:
        item_node = et.Element('dict')
        add_int_param(
            key='Track ID', parent_node=item_node, value=track_id,
        )
        items_array.append(item_node)

    playlist_node.append(items_key)
    playlist_node.append(items_array)
    return playlist_node


def param_add_factory(parent_node, default_type='string'):
    """ Returns function, configured to adding xml tag to <parent_node>

    :param parent_node: parent xml tag
    :param default_type: default type for attrs added to child xml node

    :return: <function>
    """
    type_map = {
        'integer': add_int_param,
        'string': add_string_param,
        'date': add_data_param,
    }

    def _add_param(key, value, type_=default_type):
        if not value:
            return
        func = type_map.get(type_, None)
        if not func:
            raise ValueError('Unknown type: "{}"'.format(type_))
        func(key=key, value=value, parent_node=parent_node)

    return _add_param


def add_int_param(key, value, parent_node):
    return __add_param(
        key=key, type_='integer',
        value=value, parent_node=parent_node
    )


def add_string_param(key, value, parent_node):
    return __add_param(
        key=key, type_='string',
        value=value, parent_node=parent_node
    )


def add_data_param(key, value, parent_node):
    return __add_param(
        key=key, type_='date',
        value=value, parent_node=parent_node
    )


def __add_param(key, type_, value, parent_node):
    """ Add to <parent_node> param in xml iTunes format

    <key>{key}</key><{type_}>{value}</{type_}>
    """
    parent_node.append(compile_node(text=key))
    parent_node.append(compile_node(text=value, key=type_))


def compile_node(text, key='key'):
    """ <{key}>{text}</{key}>
    """
    key_node = et.Element(key)
    key_node.text = str(text)
    return key_node
