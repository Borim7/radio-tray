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
import uuid
import logging

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    from gi.repository import Gdk
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

from .lib.common import APP_ICON_ON
from .lib import utils


drop_yes = [Gtk.TargetEntry.new(target = "drop_yes", flags = Gtk.TargetFlags.SAME_WIDGET, info = 0)]
drop_no = [Gtk.TargetEntry.new(target = "drop_no", flags = Gtk.TargetFlags.SAME_WIDGET, info = 0)]
targets = [('data',Gtk.TargetFlags.SAME_APP,0)]


class BookmarkConfiguration:

    GROUP_TYPE = 'GROUP'
    RADIO_TYPE = 'RADIO'
    SEPARATOR_TYPE = 'SEPARATOR'

    def __init__(self, dataProvider, updateFunc, standalone=False):

        self.dataProvider = dataProvider
        self.updateFunc = updateFunc
        self.standalone = standalone

        self.log = logging.getLogger('radiotray')

        # get gui objects
        gladefile = utils.load_ui_file("configBookmarks.glade")
        self.wTree = gladefile
        self.window = self.wTree.get_object("window1")
        self.list = self.wTree.get_object("treeview1")

        # edit bookmark
        self.nameEntry = self.wTree.get_object("nameEntry")
        self.nameEntryLabel = self.wTree.get_object("label1")
        self.urlEntry = self.wTree.get_object("urlEntry")
        self.urlEntryLabel = self.wTree.get_object("label2")
        self.config = self.wTree.get_object("editBookmark")
        self.radioGroup = self.wTree.get_object("radioGroup")
        self.radioGroupLabel = self.wTree.get_object("label8")

        # edit group
        self.configGroup = self.wTree.get_object("editGroup")
        self.groupNameEntry = self.wTree.get_object("groupNameEntry")
        self.parentGroup = self.wTree.get_object("parentGroup")
        self.parentGroupLabel = self.wTree.get_object("label4")

        # separator move
        self.sepMove = self.wTree.get_object("sepMove")
        self.sepGroup = self.wTree.get_object("sepGroup")

        # set icon
        self.window.set_icon_from_file(APP_ICON_ON)
        self.config.set_icon_from_file(APP_ICON_ON)
        self.configGroup.set_icon_from_file(APP_ICON_ON)
        self.sepMove.set_icon_from_file(APP_ICON_ON)

        # populate list of radios
        self.load_data()

        # config tree ui
        cell = Gtk.CellRendererText()
        tvcolumn = Gtk.TreeViewColumn(_('Radio Name'), cell)
        self.list.append_column(tvcolumn)
        tvcolumn.add_attribute(cell, 'text', 0)

        # config combo ui
        cell2 = Gtk.CellRendererText()
        self.parentGroup.pack_start(cell2, True)
        self.parentGroup.add_attribute(cell2, 'text', 0)

        # config add radio group combo ui
        cell4 = Gtk.CellRendererText()
        self.radioGroup.pack_start(cell4, True)
        self.radioGroup.add_attribute(cell4, 'text', 0)

        # separator new group combo ui
        cell3 = Gtk.CellRendererText()
        self.sepGroup.pack_start(cell3, True)
        self.sepGroup.add_attribute(cell3, 'text', 0)




        # connect events defined by gladefile
        if self.window:
            self.wTree.connect_signals(self)

        # enable drag and drop support
        self.list.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
        self.list.enable_model_drag_dest([], Gdk.DragAction.MOVE)
        print("config")
        self.list.drag_dest_add_text_targets()
        self.list.drag_source_add_text_targets()

        self.list.connect("drag_data_received", self.onDragDataReceived)
        self.list.connect("drag_data_get", self.onDataGet)

        # Connect row activation with bookmarks conf
        self.list.connect("row-activated", self.on_row_activated)

    def load_data(self):

        # the meaning of the three columns is: description, id, type
        treestore = Gtk.TreeStore(str, str, str)
        root = self.dataProvider.getRootGroup()
        self.add_group_data(root, None, treestore)
        self.list.set_model(treestore)



    #drag and drop support
    def checkSanity(self, model, source, target):
        source_path = model.get_path(source)
        target_path = model.get_path(target)
        if target_path[0:len(source_path)] == list(source_path):
            return False
        else:
            return True

    #drag and drop support
    def checkParentability(self, model, target, drop_position):

        if drop_position in (Gtk.TreeViewDropPosition.INTO_OR_BEFORE,
            Gtk.TreeViewDropPosition.INTO_OR_AFTER):

            if(model.get_value(target, 2) == self.RADIO_TYPE or
                model.get_value(target, 2) == self.SEPARATOR_TYPE):

                return False
            else:
                return True
        else:
            return True

    #drag and drop support
    def expandToPath(self, treeview, path):
        for i in range(len(path)):
            treeview.expand_row(path[:i+1], open_all=False)


    #drag and drop support
    def copyRow(self, treeview, model, source, target, drop_position):

        #source_is_expanded = treeview.row_expanded(model.get_path(source))
        new = None

        if drop_position in (Gtk.TreeViewDropPosition.INTO_OR_BEFORE,
            Gtk.TreeViewDropPosition.INTO_OR_AFTER):

            new = model.append(target, model[source][:])

        elif drop_position == Gtk.TreeViewDropPosition.BEFORE:
            parent = model.iter_parent(target)
            new = model.insert_before(parent, target, model[source][:])

        elif drop_position == Gtk.TreeViewDropPosition.AFTER:
            parent = model.iter_parent(target)
            new = model.insert_after(parent, target, model[source][:])

        else:
            print("No data copied!")
            return

        while model.iter_n_children(source) > 0:
            child = model.iter_nth_child(source, 0)
            self.copyRow(treeview, model, child, new, Gtk.TreeViewDropPosition.INTO_OR_BEFORE)

        model.remove(source)



        #if source_is_expanded:
        #    self.expandToPath(treeview, model.get_path(new))


    def onDataGet(self, widget, _context, selection, _info, _time):
        treeselection = widget.get_selection()
        model, tsIter = treeselection.get_selected()
        data = model.get_value(tsIter, 0)
        selection.set(selection.get_target(), 8, data)

    #drag and drop support
    def onDragDataReceived(self, treeview, drag_context, x, y, _selection_data, _info, eventtime):

        #check if there's a valid drop location
        if treeview.get_dest_row_at_pos(x, y) is None:
            self.log.debug("Dropped into nothing")
            return

        target_path, drop_position = treeview.get_dest_row_at_pos(x, y)
        model, source = treeview.get_selection().get_selected()
        target = model.get_iter(target_path)
        sourceName = model.get_value(source,1)
        targetName = model.get_value(target,1)

        print("source: " + sourceName + " , target: " + targetName)

        is_sane = self.checkSanity(model, source, target)
        is_parentable = self.checkParentability(model, target, drop_position)

        if is_sane and is_parentable:

            self.copyRow(treeview, model, source, target, drop_position)
            if drop_position in (Gtk.TreeViewDropPosition.INTO_OR_BEFORE,
                    Gtk.TreeViewDropPosition.INTO_OR_AFTER):
                treeview.expand_row(target_path, False)

            drag_context.finish(True, True, eventtime)

            self.dataProvider.moveToPosition(sourceName, targetName, drop_position)
        else:
            drag_context.finish(False, False, eventtime)






    def add_group_data(self, group, parent, treestore):

        tsIter = None
        if group.get('name') != 'root':
            tsIter = treestore.append(parent, [group.get('name'), group.get('name'),
                self.GROUP_TYPE])

        for item in group:

            if item.get('name') is None:
                continue

            if item.tag == 'bookmark':
                if item.get('name').startswith('[separator'):
                    treestore.append(tsIter, ['-- ' + _('Separator') + ' --',
                        item.get('name'), self.SEPARATOR_TYPE])
                else:
                    treestore.append(tsIter, [item.get('name'), item.get('name'), self.RADIO_TYPE])
            else:
                self.add_group_data(item, tsIter, treestore)

    def on_add_separator_clicked(self, _widget):
        # hack: generate a unique name
        name = '[separator-' + str(uuid.uuid4()) + ']'
        self.dataProvider.addRadio(name, name)
        self.load_data()

    def on_add_bookmark_clicked(self, _widget):

        # reset old dialog values
        self.nameEntry.set_text('')
        self.urlEntry.set_text('')
        self.config.set_title(_('Add new station'))
        self.nameEntry.grab_focus()
        self.radioGroup.show()
        self.radioGroupLabel.show()

        # populate groups
        liststore = Gtk.ListStore(str)

        for group in self.dataProvider.listGroupNames():
            liststore.append([group])
            print("group found: " + group)

        self.radioGroup.set_model(liststore)

        # default to root
        self.radioGroup.set_active(0)

        # get current selected group and set it as default
        selection = self.list.get_selection()
        (model, tsIter) = selection.get_selected()

        if type(tsIter).__name__ == 'TreeIter':
            selectedName = model.get_value(tsIter, 1)
            selectedType = model.get_value(tsIter, 2)

            if selectedType == self.GROUP_TYPE:
                groupIndex = self.dataProvider.listGroupNames().index(selectedName)
                self.radioGroup.set_active(groupIndex)

        # show dialog
        result = self.config.run()
        if result == 2:
            name = self.nameEntry.get_text()
            url = self.urlEntry.get_text()
            index = self.radioGroup.get_active()
            new_group = liststore[index][0]

            if len(name) > 0 and len(url) > 0:
                if self.dataProvider.addRadio(name, url, new_group):
                    self.load_data()
            else:
                print('No radio information provided!')
        self.config.hide()

    def on_edit_bookmark_clicked(self, _widget):

        #get current selected element
        selection = self.list.get_selection()
        (model, tsIter) = selection.get_selected()

        if type(tsIter).__name__=='TreeIter':

            selectedName = model.get_value(tsIter, 1)
            selectedType = model.get_value(tsIter, 2)

            liststore = Gtk.ListStore(str)

            for group in self.dataProvider.listGroupNames():
                liststore.append([group])
                self.log.debug('group found: "%s"', group)


            if selectedType == self.RADIO_TYPE:

                #set combo box model
                self.radioGroup.set_model(liststore)

                #get radio bookmark details
                selectedRadioUrl = self.dataProvider.getRadioUrl(selectedName)
                selectedRadio = self.dataProvider._radioExists(selectedName)
                currentGroup = selectedRadio.getparent().get("name")
                groupIndex = self.dataProvider.listGroupNames().index(currentGroup)

                # populate dialog with radio information
                self.nameEntry.set_text(selectedName)
                self.urlEntry.set_text(selectedRadioUrl)
                oldName = selectedName
                self.config.set_title(_('Edit %s') % selectedName)
                self.nameEntry.grab_focus()
                self.radioGroup.set_active(groupIndex)

                # show dialog
                result = self.config.run()

                if result == 2:
                    name = self.nameEntry.get_text()
                    url = self.urlEntry.get_text()
                    index = self.radioGroup.get_active()
                    new_group = liststore[index][0]

                    if len(name) > 0 and len(url) > 0:
                        if self.dataProvider.updateRadio(oldName, name, url):
                            model.set_value(tsIter,0,name)
                            model.set_value(tsIter,1,name)
                        if new_group != currentGroup:
                            self.dataProvider.updateElementGroup(selectedRadio, new_group)
                            self.load_data()
                    else:
                        self.log.debug('No radio information provided!')
                self.config.hide()

            elif selectedType == self.GROUP_TYPE:

                #set  combo box model
                self.parentGroup.set_model(liststore)

                #get group details
                selectedGroup = self.dataProvider._groupExists(selectedName)
                currentGroup = selectedGroup.getparent().get("name")
                groupIndex = self.dataProvider.listGroupNames().index(currentGroup)

                #populate dialog with group information
                self.groupNameEntry.set_text(selectedName)
                self.configGroup.set_title(_('Edit group'))
                oldName = selectedName
                self.parentGroup.set_active(groupIndex)

                result = self.configGroup.run()
                if result == 2:
                    name = self.groupNameEntry.get_text()
                    index = self.parentGroup.get_active()
                    new_group = liststore[index][0]


                    if len(name) > 0:
                        if self.dataProvider.updateGroup(oldName, name):
                            model.set_value(tsIter,0,name)
                            model.set_value(tsIter,1,name)
                        if new_group not in (selectedName, currentGroup):
                            self.dataProvider.updateElementGroup(selectedGroup, new_group)
                            self.load_data()
                        else:
                            self.log.debug('No group information provided')

                self.configGroup.hide()

            elif selectedType == self.SEPARATOR_TYPE:

                #Set combo box model
                self.sepGroup.set_model(liststore)

                #get radio bookmark details
                selectedRadio = self.dataProvider._radioExists(selectedName)
                currentGroup = selectedRadio.getparent().get("name")
                groupIndex = self.dataProvider.listGroupNames().index(currentGroup)

                # populate dialog with radio information
                self.sepMove.set_title(_('Edit Separator'))
                self.sepGroup.grab_focus()
                self.sepGroup.set_active(groupIndex)

                # show dialog
                result = self.sepMove.run()

                if result == 2:
                    index = self.sepGroup.get_active()
                    new_group = liststore[index][0]

                    if new_group != currentGroup:
                        self.dataProvider.updateElementGroup(selectedRadio, new_group)
                        self.load_data()

                self.sepMove.hide()

    def on_row_activated(self, widget, _row, _cell):
        self.on_edit_bookmark_clicked(widget)



    def on_remove_bookmark_clicked(self, _widget):

        #get current selected element
        selection = self.list.get_selection()
        (model, tsIter) = selection.get_selected()

        if type(tsIter).__name__=='TreeIter':

            selectedRadioName = model.get_value(tsIter,0)
            separatorFlag = model.get_value(tsIter,1)
            print(selectedRadioName + " - " + separatorFlag)

            # if separator then just remove it
            if not separatorFlag.startswith("[separator-"):

                confirmation = Gtk.MessageDialog(
                    self.window,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    _("Are you sure you want to delete \"%s\"?") % selectedRadioName
                )

                result = confirmation.run()


                if result == -8:
                    # remove from data provider
                    self.dataProvider.removeRadio(selectedRadioName)

                    # remove from gui
                    model.remove(tsIter)

                confirmation.hide()
            else:
                self.dataProvider.removeRadio(separatorFlag)
                # remove from gui
                model.remove(tsIter)



    def on_close_clicked(self, _widget):

        self.updateFunc()
        self.window.hide()

    # close the window and quit
    def on_delete_event(self, _widget, _event, _data=None):
        if self.standalone:
            Gtk.main_quit()
        return False

    def on_nameEntry_activated(self, _widget):
        self.urlEntry.grab_focus()

    def on_urlEntry_activated(self, _widget):
        self.config.response(2)

    def on_newGroupButton_clicked(self, _widget):

        # reset old dialog values
        self.groupNameEntry.set_text('')
        self.configGroup.set_title(_('Add new group'))
        self.parentGroupLabel.show()
        self.parentGroup.show()
        self.groupNameEntry.grab_focus()

        # populate parent groups
        liststore = Gtk.ListStore(str)

        for group in self.dataProvider.listGroupNames():
            liststore.append([group])
            self.log.debug('group found: "%s"', group)

        self.parentGroup.set_model(liststore)

        # default to root
        self.parentGroup.set_active(0)

        # get current selected group and set it as default
        selection = self.list.get_selection()
        (model, tsIter) = selection.get_selected()

        if type(iter).__name__=='TreeIter':
            selectedName = model.get_value(tsIter, 1)
            selectedType = model.get_value(tsIter, 2)

            if selectedType == self.GROUP_TYPE:
                groupIndex = self.dataProvider.listGroupNames().index(selectedName)
                self.parentGroup.set_active(groupIndex)

        # show dialog
        result = self.configGroup.run()
        if result == 2:

            # get group name
            name = self.groupNameEntry.get_text()

            # get parent group name
            index = self.parentGroup.get_active()
            parent_group = liststore[index][0]

            if len(name) > 0:
                if self.dataProvider.addGroup(parent_group, name):
                    self.load_data()
            else:
                self.log.debug('No group information provided!')
        self.configGroup.hide()
