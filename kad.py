#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2
gi.require_version('GtkSource', '3.0')
from gi.repository import GtkSource

import datetime
import getpass
import json
import os
import sys
import urllib

class KAD:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui.glade")
        self.builder.connect_signals(self)

        window = self.builder.get_object("main_window")
        self.location_entry = self.builder.get_object("location_entry")

        accelerators = Gtk.AccelGroup()
        window.add_accel_group(accelerators)
        key, mod = Gtk.accelerator_parse("<Control>l")
        self.location_entry.add_accelerator("grab-focus", accelerators, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>q")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, Gtk.main_quit)

        browser_window = self.builder.get_object("browser_window")
        self.browser_view = WebKit2.WebView()
        self.browser_view.connect("load-changed", self.load_changed)
        browser_window.add(self.browser_view)

        self.location_entry.set_text("http://en.wikipedia.org/wiki/AI")
        self.location_entry_activate()
        self.browser_view.get_settings().set_property("enable-developer-extras",True)

        lm = GtkSource.LanguageManager()
        self.editor_buffer = GtkSource.Buffer.new_with_language(lm.get_language("python"))
        self.filename = "kad.py"
        with open(self.filename, 'r') as f:
            self.file_data = f.read()
            self.editor_buffer.set_text(self.file_data)
        self.editor_view = GtkSource.View.new_with_buffer(self.editor_buffer)
        self.editor_view.set_auto_indent(True)
        self.editor_view.set_show_line_numbers(True)
        self.editor_view.set_highlight_current_line(True)
        self.editor_view.set_insert_spaces_instead_of_tabs(True)
        self.editor_window = self.builder.get_object("editor_window")
        self.editor_window.add(self.editor_view)
        key, mod = Gtk.accelerator_parse("<Control>s")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.save_file)
        self.notebook = self.builder.get_object("notebook")

        key, mod = Gtk.accelerator_parse("<Control>r")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.reload_kad)

        self.jan_editor = self.builder.get_object("jan_editor")
        self.jan_editor_buffer = self.builder.get_object("jan_editor_buffer")
        self.visualizer_viewport = self.builder.get_object("visualizer_viewport")

        self.visualizer_view = WebKit2.WebView()
        self.visualizer_viewport.add(self.visualizer_view)

        window.fullscreen()
        window.show_all()

        self.jan_editor.hide()
        self.visualizer_viewport.hide()

    def load(self, uri):
        self.browser_view.load_uri(uri)

    def select_tab(self, tab):
        if tab == "edit":
                self.notebook.set_current_page(1)

    def save_file(self, *args):
        text = self.get_editor_text()
        with open(self.filename, 'w') as f:
            f.write(text)
        self.file_data = text

    def ensure_saved(self):
        if self.get_editor_text() != self.file_data:
                self.save_file()

    def get_editor_text(self):
        start_iter = self.editor_buffer.get_start_iter()
        end_iter = self.editor_buffer.get_end_iter()
        return self.editor_buffer.get_text(start_iter, end_iter, True)

    def reload_kad(self, *args):
        self.ensure_saved()
        os.execl("./kad.py", "./kad.py", "edit")

    def main(self, args):
        if len(args) > 1:
                self.select_tab(args[1])
        Gtk.main()

    def main_window_delete(self, *args):
        Gtk.main_quit(*args)

    def save_button_clicked(self, *args):
        if self.jan_editor.is_visible():
            self.jan_editor.hide()
        else:
            uri = self.browser_view.get_uri()
            title = self.browser_view.get_title()
            time = str(datetime.datetime.now())
            user = getpass.getuser()
            jan = {
                'type': 'url',
                'link': uri,
                'metadata': [
                    {
                        'name': "page title",
                        'value': title
                    },
                    {
                        'name': 'retrieval time',
                        'value': time
                    },
                    {
                        'name': 'originating user',
                        'value': user
                    }
                ]}
            self.jan_editor_buffer.set_text(json.dumps(jan, sort_keys=False, indent=4))
            self.jan_editor.show()

    def visualize_button_clicked(self, *args):
        if self.visualizer_viewport.is_visible():
            self.visualizer_viewport.hide()
        else:
            self.visualizer_viewport.show()

    def location_entry_activate(self, *args):
        uri = self.location_entry.get_text()
        if not("http" in uri):
            uri = "http://" + uri
        self.load(uri)

    def load_changed(self, *args):
        if args[1] == WebKit2.LoadEvent.FINISHED:
            uri = self.browser_view.get_uri()
            visualization_uri = "http://www.infocaptor.com/bubble-my-page?url=" + \
                                urllib.quote_plus(uri) + "&size=400"
            self.location_entry.set_text(uri)
            self.visualizer_view.load_uri(visualization_uri)


kad = KAD()
kad.main(sys.argv)
