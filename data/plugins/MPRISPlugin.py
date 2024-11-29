# Copyright (C) 2024 Faidon Liambotis
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radio Tray.  If not, see <http://www.gnu.org/licenses/>.

from dbus_next import Variant
from dbus_next.constants import PropertyAccess
from dbus_next.glib import MessageBus
from dbus_next.service import ServiceInterface, dbus_property, method
from radiotray.events.EventManager import EventManager
from radiotray.lib.common import APPDIRNAME, APPNAME
from radiotray.Plugin import Plugin

# dbus_next has its own type annotations, which these ruff checks are not happy with
# ruff: noqa: F722, F821


class MediaPlayer2Interface(ServiceInterface):
    def __init__(self, provider, mediator):
        super().__init__("org.mpris.MediaPlayer2")
        self.provider = provider
        self.mediator = mediator

    @dbus_property(PropertyAccess.READ)
    def Identity(self) -> "s":
        return APPNAME

    @dbus_property(PropertyAccess.READ)
    def DesktopEntry(self) -> "s":
        return APPDIRNAME

    @dbus_property(PropertyAccess.READ)
    def CanQuit(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def CanSetFullscreen(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READWRITE)
    def Fullscreen(self) -> "b":
        return False

    @Fullscreen.setter
    def Fullscreen(self, val: "b"):
        pass

    @dbus_property(PropertyAccess.READ)
    def CanRaise(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def HasTrackList(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def SupportedUriSchemes(self) -> "as":
        return ["http", "https", "rtsp", "rtmp", "mms"]

    @dbus_property(PropertyAccess.READ)
    def SupportedMimeTypes(self) -> "as":
        return ["application/ogg", "audio/mpeg", " audio/x-flac", "audio/x-mpegurl"]


class MediaPlayer2PlayerInterface(ServiceInterface):
    def __init__(self, provider, mediator):
        super().__init__("org.mpris.MediaPlayer2.Player")
        self.provider = provider
        self.mediator = mediator

    @dbus_property(PropertyAccess.READ)
    def CanControl(self) -> "b":
        return True

    @dbus_property(PropertyAccess.READ)
    def CanGoNext(self) -> "b":
        return False

    @method()
    def Next(self):
        pass

    @dbus_property(PropertyAccess.READ)
    def CanGoPrevious(self) -> "b":
        return False

    @method()
    def Previous(self):
        pass

    @dbus_property(PropertyAccess.READ)
    def CanPlay(self) -> "b":
        return True

    @method()
    def Play(self):
        self.mediator.playLast()

    @dbus_property(PropertyAccess.READ)
    def CanPause(self) -> "b":
        return True

    @method()
    def Pause(self):
        self.mediator.stop()

    @method()
    def Stop(self):
        self.mediator.stop()

    @method()
    def PlayPause(self):
        if self.mediator.context.state == "playing" or self.mediator.context.state == "connecting":
            self.mediator.stop()
        else:
            self.mediator.playLast()

    @dbus_property(PropertyAccess.READ)
    def CanSeek(self) -> "b":
        return False

    @method()
    def Seek(self, offset: "x"):
        pass

    @method()
    def SetPosition(self, track_id: "o", position: "x"):
        pass

    @method()
    def OpenUri(self, uri: "s"):
        self.mediator.playUrl(uri)

    @dbus_property(PropertyAccess.READ)
    def PlaybackStatus(self) -> "s":
        if self.mediator.context.state == "playing" or self.mediator.context.state == "connecting":
            return "Playing"
        else:
            return "Stopped"

    @dbus_property(PropertyAccess.READWRITE)
    def LoopStatus(self) -> "s":
        return "None"

    @LoopStatus.setter
    def LoopStatus(self, loop_status: "s"):
        pass

    @dbus_property(PropertyAccess.READ)
    def Rate(self) -> "d":
        return 1.0

    @Rate.setter
    def Rate(self, playback_rate: "d"):
        pass

    @dbus_property(PropertyAccess.READ)
    def MinimumRate(self) -> "d":
        return 1.0

    @dbus_property(PropertyAccess.READ)
    def MaximumRate(self) -> "d":
        return 1.0

    @dbus_property(PropertyAccess.READWRITE)
    def Shuffle(self) -> "b":
        return False

    @Shuffle.setter
    def Shuffle(self, shuffle: "b"):
        pass

    @dbus_property(PropertyAccess.READWRITE)
    def Volume(self) -> "d":
        return self.mediator.getVolume() / 100

    @Volume.setter
    def Volume(self, volume: "d"):
        if volume < 0 or volume > 1:
            return
        self.mediator.set_volume(volume)

    @dbus_property(PropertyAccess.READ)
    def Position(self) -> "x":
        return 0

    @dbus_property(PropertyAccess.READ)
    def Metadata(self) -> "a{sv}":
        return {
            "xesam:url": Variant("s", self.provider.getRadioUrl(self.mediator.getContext().station)),
            "xesam:artist": Variant("s", self.mediator.getContext().station),
            "xesam:title": Variant("s", self.mediator.getContext().getSongInfo()),
        }

    def on_state_changed(self, data):
        self.emit_properties_changed({"PlaybackStatus": self.PlaybackStatus})

    def on_song_changed(self, data):
        self.emit_properties_changed({"Metadata": self.Metadata})

    def on_volume_changed(self, data):
        self.emit_properties_changed({"Volume": self.Volume})


class MPRISPlugin(Plugin):
    def initialize(
        self,
        name,
        eventManagerWrapper,
        eventSubscriber,
        provider,
        cfgProvider,
        mediator,
        tooltip,
    ):
        self.name = name
        self.eventManagerWrapper = eventManagerWrapper
        self.eventSubscriber = eventSubscriber
        self.provider = provider
        self.cfgProvider = cfgProvider
        self.mediator = mediator
        self.tooltip = tooltip

    def getName(self):
        return self.name

    def activate(self):
        try:
            bus = MessageBus().connect_sync()
        except Exception:
            print("Could not connect to the D-Bus Session Bus")
            return

        root_interface = MediaPlayer2Interface(self.provider, self.mediator)
        bus.export("/org/mpris/MediaPlayer2", root_interface)

        player_interface = MediaPlayer2PlayerInterface(self.provider, self.mediator)
        bus.export("/org/mpris/MediaPlayer2", player_interface)

        # translate from RadioTray events to MPRIS PropertyChanged signals
        self.eventSubscriber.bind(EventManager.SONG_CHANGED, player_interface.on_song_changed)
        self.eventSubscriber.bind(EventManager.STATE_CHANGED, player_interface.on_state_changed)
        self.eventSubscriber.bind(EventManager.VOLUME_CHANGED, player_interface.on_volume_changed)

        # these interfaces are optional and we do not implement them
        # avoid errors/backtraces when we are inevitably polled for them through GetAll()
        bus.add_message_handler(
            lambda message: any(
                (
                    "org.mpris.MediaPlayer2.TrackList" in message.body,
                    "org.mpris.MediaPlayer2.Playlists" in message.body,
                )
            )
        )

        bus.request_name_sync("org.mpris.MediaPlayer2.radiotray")
