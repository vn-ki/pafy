import json

from . import g
from .pafy import new, get_categoryname, call_gdata, fetch_decode
from .playlist import Playlist

def get_channel(channel_url, basic=False, gdata=False,
                 size=False, callback=None):
    """

    """

    return Channel(channel_url, basic, gdata, size, callback)


class Channel(object) :
    def __init__(self, channel_url, basic, gdata, size, callback) :

        #TODO
        channel_id = channel_url

        #TODO
        if not channel_id :
            err = "Unrecognized channel url : %s"
            raise ValueError(err % channel_url)

        query = {'part' : 'snippet, contentDetails, statistics',
                'id' : channel_id}
        allinfo = call_gdata('channels', query)

        ch = allinfo['items'][0]

        self.channel_id = channel_id
        self.name = ch['snippet']['title']
        self.description = ch['snippet']['description']
        self.logo = ch['snippet']['thumbnails']['default']['url']
        self.subscribers = ch['statistics']['subscriberCount']
        self._uploads = ch['contentDetails']['relatedPlaylists']['uploads']
        self._basic = basic
        self._gdata = gdata
        self._size = size
        self._callback = callback
        self._playlists = None

    @property
    def uploads(self) :
        return Playlist(self._uploads, self._basic, self._gdata, self._size, self._callback)

    @property
    def playlists(self) :
        if self._playlists != None :
            return self._playlists

        playlists = []

        query = {'part': 'snippet,contentDetails',
                'maxResults': 50,
                'channelId': self.channel_id}

        while True :
            playlistList = call_gdata('playlists', query)

            for pl in playlistList['items'] :
                pl_data = dict(
                    title = pl['snippet']['title'],
                    author = pl['snippet']['channelTitle'],
                    description = pl['snippet']['description'],
                    len = pl['contentDetails']['itemCount']
                )

                pl_obj = Playlist(pl['id'], self._basic, self._gdata, self._size, self._callback)

                pl_obj._populate_from_channel(pl_data)
                playlists.append(pl_obj)
                if self._callback:
                    self._callback("Added playlist: %s" % pl_data['title'])

            if not playlistList.get('nextPageToken'):
                break
            query['pageToken'] = playlistList['nextPageToken']

        self._playlists = playlists
        return self._playlists
