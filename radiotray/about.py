# -*- coding: utf-8 -*-
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, GdkPixbuf
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

import radiotray.lib.common as common

TRANSLATORS = _("translator-credits")

class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent = None):
        super().__init__(self, parent)
        self.set_icon_from_file(common.APP_ICON)

        self.set_program_name(common.APPNAME)
        self.set_version(common.APPVERSION)
        self.set_copyright(common.COPYRIGHTS)
        self.set_logo(GdkPixbuf.Pixbuf.new_from_file(common.APP_ICON))
        self.set_translator_credits(TRANSLATORS)
        self.set_license(common.LICENSE)
        self.set_website(common.WEBSITE)
        self.set_website_label(_("%s's Website") % common.APPNAME)
        self.set_authors(common.AUTHORS)
        self.set_artists(common.ARTISTS)

        self.connect("response", lambda self, *args: self.destroy())
        self.show_all()
