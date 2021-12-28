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
import os
import logging
from lxml import etree


class XmlConfigProvider:

    def __init__(self, filename):
        self.root = None
        self.log = logging.getLogger('radiotray')
        if os.access(filename, os.R_OK):
            self.filename = filename
        else:
            raise Exception('Configuration file not found: ' + filename)


    def loadFromFile(self):
        try:
            self.root = etree.parse(self.filename).getroot()
        except etree.XMLSyntaxError:
            raise Exception('Configuration file corrupted: ' + self.filename)


    def saveToFile(self):
        out_file = open(self.filename, "wb")
        out_file.write(etree.tostring(self.root, method='xml', encoding='UTF-8', pretty_print=True))
        out_file.close()


    def getConfigValue(self, name):
        if self.root is not None:
            result = self.root.xpath("//option[@name=$var]/@value", var=name)
            if len(result) >= 1:
                return result[0]

        return None


    def setConfigValue(self, name, value):

        setting = self._settingExists(name)

        if setting is None:
            setting = etree.SubElement(self.root, 'option')
            setting.set("name", name)
            setting.set("value", value)
        else:
            setting.set("value", value)

        self.saveToFile()

    def getConfigList(self, name):
        result = self.root.xpath("//option[@name=$var]/item", var=name)
        return [x.text for x in result]


    def setConfigList(self, name, items):
        setting = self._settingExists(name)

        if setting is None:
            setting = etree.SubElement(self.root, 'option')
            setting.set("name", name)
        else:
            self.log.debug('remove all')
            children = setting.getchildren()
            for child in children:
                self.log.debug('remove child %s', child.text)
                setting.remove(child)

        for item in items:
            it = etree.SubElement(setting, 'item')
            it.text = item

        self.saveToFile()


    def _settingExists(self, name):
        """Return the requested setting or None if it does not exists"""
        setting = None

        try:
            setting = self.root.xpath("//option[@name=$var]", var=name)[0]
        except IndexError:
            # Setting wasn't found
            self.log.warning('Could not find setting with the name "%s".', name)

        return setting
