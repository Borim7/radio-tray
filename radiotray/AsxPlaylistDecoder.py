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
from lxml import etree
from io import StringIO
import logging
import requests

class AsxPlaylistDecoder:

    def __init__(self):
        self.log = logging.getLogger('radiotray')
        self.log.debug('ASX-familiy playlist decoder')


    def isStreamValid(self, contentType, firstBytes):

        if(('audio/x-ms-wax' in contentType or 'video/x-ms-wvx' in contentType or 'video/x-ms-asf' in contentType or 'video/x-ms-wmv' in contentType) and firstBytes.strip().lower().startswith(b'<asx')):
            self.log.info('Stream is readable by ASX Playlist Decoder')
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

        #ugly hack to normalize the XML
        for element in root.iter():

            tmp = element.tag
            element.tag = tmp.lower()

            for key in element.attrib.keys():
                element.attrib[key.lower()] = element.attrib[key]


        result = root.xpath("//ref/@href")

        if (len(result) > 0):

            for i in range(1,len(result)):

                tmp = result[i]
                if (tmp.endswith("?MSWMExt=.asf")):
                    result[i] = tmp.replace("http", "mms")
            return result
        else:
            return []
