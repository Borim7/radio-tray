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
import logging
import traceback
import requests
from .lib.common import APPNAME
from .lib.common import getDefaultHttpHeader, ICON_FILE

class NotificationManager:

    def __init__(self, eventManagerWrapper):
        self.eventManagerWrapper = eventManagerWrapper
        self.log = logging.getLogger('radiotray')
        self.lastState = None

    def on_state_changed(self, data):

        state = data['state']

        if(state == 'playing' and state != self.lastState):
            station = data['station']
            self.eventManagerWrapper.notify(_('Radio Tray Playing'), station)

        self.lastState = state



    def on_song_changed(self, data):

        self.log.debug(data)

        station = data['station']
        msgTitle = "%s - %s" % (APPNAME , station)
        msg = None

        if 'artist' in list(data.keys()) and 'title' in list(data.keys()):
            artist = data['artist']
            title = data['title']
            msg = "%s - %s" % (artist, title)
        elif 'artist' in list(data.keys()):
            msg = data['artist']
        elif 'title' in list(data.keys()):
            msg = data['title']

        if('homepage' in list(data.keys()) and (data['homepage'].endswith('png') or
            data['homepage'].endswith('jpg'))):

            #download image
            try:
                resp = requests.get(data['homepage'], headers=getDefaultHttpHeader())

                try:
                    with open(ICON_FILE,'wb') as f:
                        f.write(resp.content)
                except OSError:
                    self.log.warning('Error saving icon')

                self.eventManagerWrapper.notify_icon(msgTitle, msg, ICON_FILE)

            except OSError:
                traceback.print_exc()
                self.eventManagerWrapper.notify(msgTitle, msg)
        else:
            self.eventManagerWrapper.notify(msgTitle, msg)

    def on_station_error(self, data):

        self.eventManagerWrapper.notify(_('Radio Error'), str(data['error']))

    def on_bookmarks_reloaded(self, data):

        self.eventManagerWrapper.notify(_("Bookmarks Reloaded"), _("Bookmarks Reloaded"))
