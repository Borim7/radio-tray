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

import sys
import os
from shutil import move, copy2
import logging
import logging.handlers

import dbus.mainloop.glib

from .XmlDataProvider import XmlDataProvider
from .XmlConfigProvider import XmlConfigProvider
from .AudioPlayerGStreamer import AudioPlayerGStreamer
from .SysTray import SysTray
from .StateMediator import StateMediator
from .NotificationManager import NotificationManager
from .events.EventManager import EventManager
from .events.EventMngNotificationWrapper import EventMngNotificationWrapper
from .events.EventSubscriber import EventSubscriber
from .DbusFacade import DbusFacade
from .TooltipManager import TooltipManager
from .PluginManager import PluginManager
from .lib.common import USER_CFG_PATH, CFG_NAME, OLD_USER_CFG_PATH,\
    DEFAULT_RADIO_LIST, OPTIONS_CFG_NAME, DEFAULT_CONFIG_FILE,\
    USER_PLUGIN_PATH, LOGFILE
from .GuiChooserConfiguration import GuiChooserConfiguration


class RadioTray:

    def __init__(self, url=None):
        self.logger = None

        self.loadConfiguration()

        self.logger.info('Starting Radio Tray...')

        # load configuration

        # load bookmarks data provider and initializes it
        self.provider = XmlDataProvider(self.filename)
        self.provider.loadFromFile()

        # load config data provider and initializes it
        self.cfg_provider = XmlConfigProvider(self.cfg_filename)
        self.cfg_provider.loadFromFile()

        # load default config data provider and initializes it
        self.default_cfg_provider = XmlConfigProvider(self.default_cfg_filename)
        self.default_cfg_provider.loadFromFile()

        # load Event Manager
        eventManager = EventManager()
        eventManagerWrapper = EventMngNotificationWrapper(eventManager)

        # mediator
        self.mediator = StateMediator(self.provider, self.cfg_provider, eventManager)

        # load audio player
        self.audio = AudioPlayerGStreamer(self.mediator, self.cfg_provider, eventManager)

        # tooltip manager
        tooltipManager = TooltipManager()
        self.logger.debug("Tooltip manager initialized.")

        # chooser
        if url == '--config':
            chooser = GuiChooserConfiguration()
            gui_engine = chooser.run()
            self.cfg_provider.setConfigValue("gui_engine", gui_engine)
            url = None
        # load gui
        self.systray = SysTray(self.mediator, self.provider, self.cfg_provider,
            self.default_cfg_provider, eventManager, tooltipManager)
        self.logger.debug("GUI initialized")


        # notification manager
        self.notifManager = NotificationManager(eventManagerWrapper)

        # bind events
        eventSubscriber = EventSubscriber(eventManager)
        eventSubscriber.bind(EventManager.STATE_CHANGED, self.mediator.on_state_changed)
        eventSubscriber.bind(EventManager.STATE_CHANGED, self.systray.on_state_changed)
        eventSubscriber.bind(EventManager.STATE_CHANGED, self.notifManager.on_state_changed)
        eventSubscriber.bind(EventManager.SONG_CHANGED, self.notifManager.on_song_changed)
        eventSubscriber.bind(EventManager.SONG_CHANGED, self.mediator.on_song_changed)
        eventSubscriber.bind(EventManager.SONG_CHANGED, self.systray.on_song_changed)
        eventSubscriber.bind(EventManager.STATION_ERROR, self.notifManager.on_station_error)
        eventSubscriber.bind(EventManager.VOLUME_CHANGED, self.systray.on_volume_changed)
        eventSubscriber.bind(EventManager.BOOKMARKS_RELOADED, self.notifManager.on_bookmarks_reloaded)

        # config mediator
        self.mediator.init(self.audio)


        # start dbus facade (can be tested via testdbus script)
        self._dbus = DbusFacade(self.provider, self.mediator)

    #load plugin manager
        self.pluginManager = PluginManager(eventManagerWrapper, eventSubscriber,
            self.provider, self.cfg_provider, self.mediator, tooltipManager,
            self.systray.getPluginMenu())
        self.systray.setPluginManager(self.pluginManager)
        self.pluginManager.discoverPlugins()
        self.pluginManager.activatePlugins()

        if url is not None:
            if url == "--resume":
                self.mediator.playLast()
            else:
                self.mediator.playUrl(url)
        # start app
        self.systray.run()


    def loadConfiguration(self):

        if not os.path.exists(USER_CFG_PATH):
            #self.logger.info("user's directory created")
            os.mkdir(USER_CFG_PATH)

        if not os.path.exists(USER_PLUGIN_PATH):
            os.mkdir(USER_PLUGIN_PATH)

        self.configLogging()

        self.logger.debug("Loading configuration...")

        self.filename = os.path.join(USER_CFG_PATH, CFG_NAME)

        self.cfg_filename = os.path.join(USER_CFG_PATH, OPTIONS_CFG_NAME)

        self.default_cfg_filename = DEFAULT_CONFIG_FILE

        if not os.access(self.filename, os.F_OK): # If bookmarks file doesn't exist

            self.logger.warning('bookmarks file could not be found. Using default...')

            #check if it exists an old bookmark file, and then move it to the new location
            oldfilename = os.path.join(OLD_USER_CFG_PATH, CFG_NAME)
            if os.access(oldfilename, os.R_OK|os.W_OK):

                self.logger.info(
                    'Found old bookmark configuration and moved it to new location: %s',
                     USER_CFG_PATH)
                move(oldfilename, self.filename)
                os.rmdir(OLD_USER_CFG_PATH)

            else:
                self.logger.info('Copying default bookmarks file to user directory')
                copy2(DEFAULT_RADIO_LIST, self.filename)
                os.chmod(self.filename, 0o644)

        if not os.access(self.cfg_filename, os.R_OK|os.W_OK):

            self.logger.warning('Configuration file not found. Copying default configuration file to user directory')
            copy2(DEFAULT_CONFIG_FILE, self.cfg_filename)
            os.chmod(self.filename, 0o644)


    def configLogging(self):
        # config logging
        self.logger = logging.getLogger('radiotray')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=2000000, backupCount=1)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

def main(argv):
    dbus.mainloop.glib.threads_init()

    basedir = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(os.path.join(basedir, "radiotray.py")):
        if os.path.exists(os.path.join(os.getcwd(), "radiotray.py")):
            basedir = os.getcwd()
    sys.path.insert(0, basedir)
    os.chdir(basedir)

    if len(argv) == 1:
        print("Trying to load URL: " + argv[0])

        try:
            bus = dbus.SessionBus()
            radiotray = bus.get_object('net.sourceforge.radiotray', '/net/sourceforge/radiotray')


            if argv[0] == '--config':
                print("Radio Tray already running.")
            else:
                print("Setting current radio through DBus...")

                playUrl = radiotray.get_dbus_method('playUrl', 'net.sourceforge.radiotray')
                playUrl(argv[0])

        except dbus.DBusException:
            RadioTray(argv[0])
    else:
        RadioTray()

if __name__ == "__main__":
    radio = RadioTray()
