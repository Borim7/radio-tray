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


class EventSubscriber:

    def __init__(self, eventManager):
    
        self.eventManager = eventManager

    def bind(self, event, callback):
    
        observersList = self.eventManager.getObserversMap()[event]
        observersList.append(callback)
        
        
    def unbind(self, event, observer):
    
        observersList = self.eventManager.getObserversMap()[event]
        try:
            observersList.remove(observer)
        except:
            print "no observer in list"