from lxml import etree as et
from random import sample
from .utils import Sequence, tostring, strand, intrand


__track_id = Sequence()
__playlist_id = Sequence()


def root_xml():  # TODO must be parametrized
    """ Returns full iTunes xml
    """
    root = et.Element('plist', attrib={'version': "1.0"})
    data = et.Element('dict')

    _add_param = param_add_factory(parent_node=data)

    _add_param('Major Version', 1, type_='integer')
    _add_param('Minor Version', 1, type_='integer')
    _add_param('Application Version', '12.7.3.46')
    _add_param('Date', '2018-04-21T15:04:31Z', type_='date')  # TODO format now
    _add_param('Features', 5, type_='integer')
    _add_param('Library Persistent ID', strand(10))

    track_key_node, track_container = xml_tracks(cnt=6)  # TODO magic nums
    data.append(track_key_node)
    data.append(track_container)

    plst_key_node, playlist_container = xml_playlists(cnt=2)
    data.append(plst_key_node)
    data.append(playlist_container)

    root.append(data)

    return root


def xml_tracks(cnt):
    """  Returns <cnt> pair of tags (track id, track), represents iTunes tracks
    """
    key_node = compile_node(text='Tracks')
    track_container = et.Element('dict')
    for _ in range(cnt):  # TODO using artists and albums pool
        id_node, track_node = xml_track(  # TODO add params prefix
            {'title': strand(7), 'artist': strand(5), 'album': strand(6)}
        )
        track_container.append(id_node)
        track_container.append(track_node)
    return key_node, track_container


def xml_track(track_dict, check_not_none=True):  # TODO support more attributes
    """ Returns two tags, represents iTunes track id and track

    :param track_dict: {
        'title': <title>,
        'artist': <artist>,
        'album': <album>,  # nullable
    }
    :param check_not_none: checking <title> and <artist> dict keys cannot be None

    :return tuple(<id_node>, <track_node>)
    """
    if check_not_none:
        for key in ('title', 'artist'):
            if key not in track_dict:
                raise ValueError('"{}" cannot be None'.format(key))

    track_id = __track_id.next
    id_node = compile_node(text=track_id)

    track_node = et.Element('dict')

    _add_param = param_add_factory(parent_node=track_node)

    _add_param(key='Track ID', value=track_id, type_='integer')
    _add_param(key='Name', value=track_dict.get('title', None))
    _add_param(key='Artist', value=track_dict.get('artist', None))
    _add_param(key='Album', value=track_dict.get('album', None))

    return id_node, track_node


def xml_playlists(cnt):
    """ Retunrs <cnt> pairs of tags (playlist id, playlist), represents iTunes playlist
    """
    key_node = compile_node(text='Playlists')
    playlist_container = et.Element('array')
    for _ in range(cnt):  # TODO add name prefix
        playlist = xml_playlist(name=strand(10), track_cnt=intrand(2, 4))
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

    available_ids = sample(range(__track_id.current), track_cnt)
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


if __name__ == '__main__':  # TODO move to test module
    xml = root_xml()
    string = tostring(xml)
    print(string)
