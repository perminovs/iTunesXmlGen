import os
from collections import defaultdict
import unittest
import tempfile
from itunesxmlgen import generate_xml
from itunesxmlgen.utils import tostring, strand, intrand
from libpytunes import Library


def tmp_file(path, text):
    with open(path, mode='w') as f:
        f.write(text)


class XmlTest(unittest.TestCase):
    def setUp(self):
        """ Prepare tml file path
        """
        self.path = os.path.join(tempfile.gettempdir(), strand(10))

    def tearDown(self):
        """ Remove tmp file by path, initialized in setUp method
        """
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass

    def __generate(self, **kwargs):
        """ Generate xml with **kwargs, save to tmp file, init parser

        :return: <iTunes xml parser object>
        """
        xml = generate_xml(**kwargs)
        tmp_file(path=self.path, text=tostring(xml))
        return Library(itunesxml=self.path)

    def test_simple(self):
        """ Test xml will be generate with given params
        """
        tracks_cnt = intrand(100, 200)
        artists_cnt = intrand(100, tracks_cnt)
        playlists_cnt = intrand(10, 20)
        playlist_fill_rate = intrand(5, 50)
        playlist_fill_variety = 0

        lib = self.__generate(
            tracks_cnt=tracks_cnt,
            artists_cnt=artists_cnt,
            playlists_cnt=playlists_cnt,
            playlist_fill_rate=playlist_fill_rate,
            playlist_fill_variety=playlist_fill_variety,
        )

        tracks = lib.songs.values()
        self.assertEqual(len(tracks), tracks_cnt)

        artists = {track.artist for track in tracks}
        self.assertLessEqual(len(artists), artists_cnt)

        playlists = lib.getPlaylistNames()
        self.assertEqual(len(playlists), playlists_cnt)

        for playlist_name in playlists:
            playlist = lib.getPlaylist(playlistName=playlist_name)
            self.assertEqual(len(playlist.tracks), playlist_fill_rate)

    def test_variety(self):
        """ Test `playlist_fill_variety` param
        """
        tracks_cnt = intrand(100, 200)
        artists_cnt = intrand(100, tracks_cnt)
        playlists_cnt = intrand(10, 20)
        playlist_fill_rate = intrand(10, 50)
        playlist_fill_variety = intrand(1, 9)

        lib = self.__generate(
            tracks_cnt=tracks_cnt,
            artists_cnt=artists_cnt,
            playlists_cnt=playlists_cnt,
            playlist_fill_rate=playlist_fill_rate,
            playlist_fill_variety=playlist_fill_variety,
        )

        for playlist_name in lib.getPlaylistNames():
            playlist = lib.getPlaylist(playlistName=playlist_name)
            self.assertAlmostEqual(
                first=len(playlist.tracks),
                second=playlist_fill_rate,
                delta=playlist_fill_variety,
            )

    def test_no_playlist(self):
        """ Test xml with no playlists generate
        """
        lib = self.__generate(playlists_cnt=0)
        self.assertEqual(lib.getPlaylistNames(), [])
        self.assertNotEquals(lib.songs, {})

    def test__invalid_params__negative_tracks_cnt(self):
        """ Test `generate_xml` raise when invalid params are given:

        tracks_cnt < 0
        """
        tracks_cnt = intrand(-20, -10)
        with self.assertRaises(expected_exception=ValueError) as exc:
            self.__generate(tracks_cnt=tracks_cnt)

        err_msg = 'Count of Tracks ({value}) must be positive'.format(
            value=tracks_cnt)
        self.assertEqual(exc.exception.args[0], err_msg)

    def test_invalid_params__playlist_tracks(self):
        """ Test `generate_xml` raise when invalid params are given:

        playlist_fill_rate > tracks_cnt
        """
        tracks_cnt = intrand(10, 20)
        playlist_fill_rate = intrand(100, 200)
        with self.assertRaises(expected_exception=ValueError) as exc:
            self.__generate(
                tracks_cnt=tracks_cnt,
                playlist_fill_rate=playlist_fill_rate
            )

        err_msg = (
            '{small_name} ({small}) must be less than '
            '{big_name} ({big})'.format(
                small=playlist_fill_rate, big=tracks_cnt,
                small_name='Count of Tracks in Playlist',
                big_name='Count of Tracks',
            )
        )
        self.assertEqual(exc.exception.args[0], err_msg)

    def test_invalid_params__rate_variety(self):
        """ Test `generate_xml` raise when invalid params are given:

        playlist_fill_variety > playlist_fill_rate
        """
        tracks_cnt = intrand(100, 200)
        playlist_fill_rate = intrand(5, 10)
        playlist_fill_variety = intrand(15, 30)
        with self.assertRaises(expected_exception=ValueError) as exc:
            self.__generate(
                tracks_cnt=tracks_cnt,
                playlist_fill_rate=playlist_fill_rate,
                playlist_fill_variety=playlist_fill_variety,
            )

        err_msg = (
            '{small_name} ({small}) must be less than '
            '{big_name} ({big})'.format(
                small=playlist_fill_variety, big=playlist_fill_rate,
                small_name='Variety of Playlist filling',
                big_name='Count of Playlists',
            )
        )
        self.assertEqual(exc.exception.args[0], err_msg)

    def test_invalid_params__artists_tracks(self):
        """ Test `generate_xml` raise when invalid params are given:

        artists_cnt > tracks_cnt
        """
        tracks_cnt = intrand(5, 10)
        artists_cnt = intrand(100, 200)
        with self.assertRaises(expected_exception=ValueError) as exc:
            self.__generate(
                tracks_cnt=tracks_cnt,
                artists_cnt=artists_cnt,
            )

        err_msg = (
            '{small_name} ({small}) must be less than '
            '{big_name} ({big})'.format(
                small=artists_cnt, big=tracks_cnt,
                small_name='Count of Artists',
                big_name='Count of Tracks',
            )
        )
        self.assertEqual(exc.exception.args[0], err_msg)

    def test__artist_cnt_equal(self):
        """ Test count of Artists in generated xml equals to `artist_cnt` param
        """
        cnt = intrand(100, 150)
        tracks_cnt, artists_cnt = cnt, cnt
        lib = self.__generate(tracks_cnt=tracks_cnt, artists_cnt=artists_cnt)

        artists = {track.artist for track in lib.songs.values()}
        self.assertEqual(len(artists), artists_cnt)

    def test__artist_cnt_distribution_smoothly(self):
        """ Test Artist to Track bind.

        `artist_cnt` = 2, `track_cnt` = 100 -> each Artists should have 50 tracks
        """
        tracks_cnt, artists_cnt = 100, 2
        lib = self.__generate(tracks_cnt=tracks_cnt, artists_cnt=artists_cnt)

        artists = defaultdict(int)
        for track in lib.songs.values():
            artists[track.artist] += 1
        self.assertEqual(tuple(artists.values()), (50, 50))

    def test__artist_cnt_distribution_not_smoothly(self):
        """ Test Artist to Track bind.

        `artist_cnt` = 60, `track_cnt` = 90 -> Artists distribution should be:
        60 artists: have 2 tracks
        30 artists: have 1 track
        """
        tracks_cnt, artists_cnt = 90, 60
        lib = self.__generate(tracks_cnt=tracks_cnt, artists_cnt=artists_cnt)

        artists = defaultdict(int)
        for track in lib.songs.values():
            artists[track.artist] += 1
        self.assertEqual(set(artists.values()), {1, 2})
