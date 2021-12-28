##########################################################################
# Copyright 2009 Carlos Ribeiro
#
# This file is part of Radio Tray
#
# Radio Tray is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 1 of the License, or
# (at your option) any later version.
#
# Radio Tray is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radio Tray.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################

from io import StringIO
import logging
import requests

from lxml import etree
from .lib.common import getDefaultHttpHeader


class XspfPlaylistDecoder:

    def __init__(self):
        self.log = logging.getLogger('radiotray')
        self.log.debug('XSPF playlist decoder')


    def isStreamValid(self, contentType, _firstBytes):

        if 'application/xspf+xml' in contentType:
            self.log.info('Stream is readable by XSPF Playlist Decoder')
            return True
        else:
            return False



    def extractPlaylist(self,  url):

        self.log.info('Downloading playlist...')

        resp = requests.get(url, headers=getDefaultHttpHeader())

        self.log.info('Playlist downloaded')
        self.log.info('Decoding playlist...')

        parser = etree.XMLParser(recover=True)
        root = etree.parse(StringIO(resp.text),parser)

        elements = root.xpath("//xspf:track/xspf:location",
            namespaces={'xspf':'http://xspf.org/ns/0/'})

        result = []
        for r in elements:
            result.append(r.text)

        if len(result) > 0:
            return result
        else:
            return None
