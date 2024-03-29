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
import logging

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    from gi.repository import Gdk
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

from .BookmarkConfiguration import BookmarkConfiguration
from .PluginConfiguration import PluginConfiguration
from .lib.common import APPVERSION
from .about import AboutDialog
from .GuiChooserConfiguration import GuiChooserConfiguration
from .events.EventManager import EventManager
from .SysTrayGui import SysTrayGui
from .AppIndicatorGui import AppIndicatorGui
from .Context import Context


class AboutWindow:
    def __init__(self, dialog_class):
        self.dialog = None
        self.dialog_class = dialog_class

    def on_dialog_destroy(self):
        self.dialog = None

    def show(self, parent = None):
        if self.dialog:
            self.dialog.present()
        else:
            if parent:
                self.dialog = self.dialog_class(parent)
            else:
                self.dialog = self.dialog_class()
            self.dialog.connect("destroy", lambda *args: self.on_dialog_destroy())

about = AboutWindow(AboutDialog)

def about_dialog(parent=None):
    about.show(parent)



class SysTray:

    def __init__(self, mediator, provider, cfg_provider, default_cfg_provider, eventManager,
        tooltipManager):

        self.version = APPVERSION
        self.mediator = mediator
        self.eventManager = eventManager
        self.log = logging.getLogger('radiotray')
        self.pluginManager = None

        # initialize data provider
        self.provider = provider
        self.cfg_provider = cfg_provider
        self.tooltip = tooltipManager

        self.ignore_toggle = False

        # execute gui chooser
        try:
            gi.require_version('AppIndicator3', '0.1')
            from gi.repository import AppIndicator3
            self.gui_engine = self.cfg_provider.getConfigValue("gui_engine")
            if self.gui_engine is None:
                self.gui_engine = default_cfg_provider.getConfigValue("gui_engine")

            if self.gui_engine is None or self.gui_engine == "chooser":
                self.log.debug('show chooser')
                chooser = GuiChooserConfiguration()
                self.gui_engine = chooser.run()

            self.cfg_provider.setConfigValue("gui_engine", self.gui_engine)

        except ImportError:
            self.log.debug('No appindicator support found. Choosing notification area...')
            self.gui_engine = "systray"



        if self.gui_engine == "appindicator":
            self.app_indicator_enabled  = True
        else:
            self.app_indicator_enabled = False
            self.cfg_provider.setConfigValue("enable_application_indicator_support", "false")

        if self.app_indicator_enabled:
            self.log.debug('App Indicator selected')
            self.gui = AppIndicatorGui(self, self.mediator, self.cfg_provider, self.provider)

        else:
            self.log.debug('Systray selected')
            self.gui = SysTrayGui(self, self.mediator, self.cfg_provider, self.provider)

        self.tooltip.setGui(self.gui)
        self.tooltip.addSource(self.gui.getCommonTooltipData)

        self.gui.buildMenu()


###### Action Events #######

    def scroll(self, _widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            self.mediator.volume_up()

        if event.direction == Gdk.ScrollDirection.DOWN:
            self.mediator.volume_down()

    def volume_up(self, _menu_item):
        self.mediator.volume_up()

    def volume_down(self, _menu_item):
        self.mediator.volume_down()


    def on_preferences(self, _data):
        config = BookmarkConfiguration(self.provider, self.update_radios)

    def on_quit(self, _data):
        self.log.info('Exiting...')
        Gtk.main_quit()

    def on_about(self, _data):
        about_dialog(parent=None)

    def on_turn_on_off(self, _data):
        if self.mediator.context.state == 'playing' or self.mediator.context.state == 'connecting':
            self.mediator.stop()
        else:
            self.mediator.play(self.mediator.context.station)

    def on_start(self, _data, radio):
        self.mediator.context.resetSongInfo()
        self.mediator.play(radio)


    def updateTooltip(self):
        self.tooltip.update()


    def update_radios(self):
        self.gui.update_radios()


    def run(self):
        Gdk.threads_init()
        Gdk.threads_enter()
        Gtk.main()


    def reload_bookmarks(self, _data):
        self.provider.loadFromFile()
        self.update_radios()
        self.eventManager.notify(EventManager.BOOKMARKS_RELOADED, {})


    def on_state_changed(self, data):

        if(data['state'] == Context.STATE_PAUSED and self.mediator.context.station == Context.UNKNOWN_RADIO):
            self.mediator.context.station = ''

        self.gui.state_changed(data)
        self.updateTooltip()

    def on_volume_changed(self, _volume):
        self.updateTooltip()

    def on_song_changed(self, _data):
        self.updateTooltip()


    def on_plugin_preferences(self, _data):
        config = PluginConfiguration(self.pluginManager, self.cfg_provider)


    def getPluginMenu(self):
        return self.gui.getPluginMenu()

    def setPluginManager(self, pluginManager):
        self.pluginManager = pluginManager
