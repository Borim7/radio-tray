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
from .lib.common import getDefaultHttpHeader
import logging
import requests

class PlsPlaylistDecoder:

    def __init__(self):
        self.log = logging.getLogger('radiotray')
        self.log.debug('PLS playlist decoder')
        

    def isStreamValid(self, contentType, firstBytes):

        if(('audio/x-scpls' in contentType) or ('application/pls+xml' in contentType) or (firstBytes.strip().lower().startswith(b'[playlist]'))):
            self.log.info('Stream is readable by PLS Playlist Decoder')
            return True
        else:
            return False



    def extractPlaylist(self,  url):
            
            self.log.info('Downloading playlist...')
            
            resp = requests.get(url, headers=getDefaultHttpHeader())
            
            self.log.info('Playlist downloaded')
            self.log.info('Decoding playlist...')
            
            playlist = []
            lines = resp.text.splitlines()
            for line in lines:

                if line.startswith("File") == True:

                        fields = line.split("=", 1)
                        playlist.append(fields[1])
      
            
            return playlist
            
            
