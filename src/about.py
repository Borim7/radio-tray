# -*- coding: utf-8 -*-
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
from lib import i18n
import lib.common as common


def on_email(about, mail):
    Gtk.show_uri(Gdk.Screen(), "mailto:%s" % mail, 0L)

def on_url(about, link):
    Gtk.show_uri(Gdk.Screen(), link, 0L)

#Gtk.about_dialog_set_email_hook(on_email)
#Gtk.about_dialog_set_url_hook(on_url)

TRANSLATORS = _("translator-credits")

class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent = None):
        GObject.GObject.__init__(self)
        self.set_icon_from_file(common.APP_ICON)

        self.set_name(common.APPNAME)
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
