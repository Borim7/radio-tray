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
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version('Gst', '1.0')

    from gi.repository import GLib
    from gi.repository import GObject
    GObject.threads_init()
    from gi.repository import Gst
    Gst.init(None)
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

from .StreamDecoder import StreamDecoder
from .lib.common import USER_AGENT
from .events.EventManager import EventManager


class AudioPlayerGStreamer:

    def __init__(self, mediator, cfg_provider, eventManager):
        self.mediator = mediator
        self.eventManager = eventManager
        self.decoder = StreamDecoder(cfg_provider)
        self.playlist = []
        self.retrying = False

        self.log = logging.getLogger('radiotray')

        # init player
        self.log.debug("Initializing gstreamer...")
        self.souphttpsrc = Gst.ElementFactory.make("souphttpsrc", "source")
        self.souphttpsrc.set_property("user-agent", USER_AGENT)

        self.log.debug("Loading playbin...")
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)

        #buffer size
        bufferSizeCfg = cfg_provider.getConfigValue("buffer_size")
        if bufferSizeCfg is not None:
            bufferSize = int(bufferSizeCfg)
            if bufferSize > 0:
                self.log.debug("Setting buffer size to %i", bufferSize)
                self.player.set_property("buffer-size", bufferSize)


        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        self.log.debug("GStreamer initialized.")

    def start(self, uri):

        urlInfo = self.decoder.getMediaStreamInfo(uri)

        if urlInfo is not None and urlInfo.isPlaylist():
            self.playlist = self.decoder.getPlaylist(urlInfo)
            if len(self.playlist) == 0:
                self.log.warning('Received empty playlist!')
                self.mediator.stop()
                self.eventManager.notify(EventManager.STATION_ERROR,
                    {'error':"Received empty stream from station"})
            self.log.debug(self.playlist)
            self.playNextStream()

        elif urlInfo is not None and not urlInfo.isPlaylist():
            self.playlist = [urlInfo.getUrl()]
            self.playNextStream()

        else:
            self.stop()
            self.eventManager.notify(EventManager.STATION_ERROR,
                {'error':"Couldn't connect to radio station"})


    def playNextStream(self):
        if len(self.playlist) > 0:
            stream = self.playlist.pop(0)
            self.log.info('Play "%s"', stream)

            urlInfo = self.decoder.getMediaStreamInfo(stream)
            if urlInfo is not None and not urlInfo.isPlaylist():
                self.playStream(stream)
            elif urlInfo is not None and urlInfo.isPlaylist():
                self.playlist = self.decoder.getPlaylist(urlInfo) + self.playlist
                self.playNextStream()
            elif urlInfo is None:
                self.playNextStream()
        else:
            self.stop()
            self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'paused'})
        self.mediator.updateVolume(self.player.get_property("volume"))


    def playStream(self, uri):
        self.player.set_property("uri", uri)
        self.player.set_state(Gst.State.PAUSED) # buffer before starting playback

    def stop(self):
        self.player.set_state(Gst.State.NULL)
        self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'paused'})

    def volume_up(self, volume_increment):
        self.player.set_property("volume", min(self.player.get_property("volume") +
            volume_increment, 1.0))
        self.mediator.updateVolume(self.player.get_property("volume"))

    def volume_down(self, volume_increment):
        self.player.set_property("volume", max(self.player.get_property("volume") -
            volume_increment, 0.0))
        self.mediator.updateVolume(self.player.get_property("volume"))

    def on_message(self, _bus, message):
        t = message.type

        stru = message.get_structure()
        if stru is not None:
            name = stru.get_name()
            if name == 'redirect':
                self.log.info("redirect received")
                self.player.set_state(Gst.State.NULL)
                stru.foreach(self.redirect, None)



        if t == Gst.MessageType.EOS:
            self.log.debug("Received MESSAGE_EOS")
            self.player.set_state(Gst.State.NULL)
            self.playNextStream()
        elif t == Gst.MessageType.BUFFERING:
            percent = message.parse_buffering()
            if percent < 100:
                self.log.debug("Buffering %s", percent)
                self.player.set_state(Gst.State.PAUSED)
            else:
                self.player.set_state(Gst.State.PLAYING)
        elif t == Gst.MessageType.ERROR:
            self.log.debug("Received MESSAGE_ERROR")
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            self.log.warning(err)
            self.log.warning(debug)

            if len(self.playlist)>0:
                self.playNextStream()
            else:
                self.eventManager.notify(EventManager.STATION_ERROR, {'error':debug})

        elif t == Gst.MessageType.STATE_CHANGED:
            oldstate, newstate, unused_pending = message.parse_state_changed()
            self.log.debug(("Received MESSAGE_STATE_CHANGED (%s -> %s)"), oldstate, newstate)

            if newstate == Gst.State.PLAYING:
                self.retrying = False
                station = self.mediator.getContext().station
                self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'playing',
                    'station':station})
            elif oldstate == Gst.State.PLAYING and newstate == Gst.State.PAUSED:
                self.log.info("Received PAUSE state.")

                if not self.retrying:
                    self.retrying = True
                    GLib.timeout_add(20000, self.checkTimeout, None)
                    self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'paused'})



        elif t == Gst.MessageType.TAG:

            taglist = message.parse_tag()

            #for (tag, value) in taglist.items():
            #    print "TT: " + tag + " - " + value

            (present, value) = taglist.get_string('title')

            if present:
                metadata = {}
                station = self.mediator.getContext().station
                metadata['title'] = value
                metadata['station'] = station

                self.eventManager.notify(EventManager.SONG_CHANGED, metadata)

            #if there is no song information, there's no point in triggering song change event
            #if('artist' in taglist.keys() or 'title' in taglist.keys()):
            #    station = self.mediator.getContext().station
            #    metadata = {}

            #    for key in taglist.keys():
            #        metadata[key] = taglist[key]

            #    metadata['station'] = station

            #    self.eventManager.notify(EventManager.SONG_CHANGED, metadata)

        return True

    def redirect(self, name, value, _data):
        if name == 'new-location':
            self.start(value)
        return True


    def checkTimeout(self, _data):
        self.log.debug("Checking timeout...")
        if self.retrying:
            self.log.info("Timed out. Retrying...")
            uri = self.player.get_property("uri")
            self.playStream(uri)
        else:
            self.log.info("Timed out, but not retrying anymore")

        # no need to repeat timeout checks
        return False
