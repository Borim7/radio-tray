##########################################################################
# Copyright 2014 Matthias Hofmann
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

from radiotray.Plugin import Plugin


class AutoPlayPlugin(Plugin):

    def activate(self):
        self.mediator.playLast()

    def on_menu(self, data):
        # empty method needed to avoid crash, Plugin class does not provide a default
        pass
