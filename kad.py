#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2
gi.require_version('GtkSource', '3.0')
from gi.repository import GtkSource
gi.require_version('EvinceDocument', '3.0')
from gi.repository import EvinceDocument
gi.require_version('EvinceView', '3.0')
from gi.repository import EvinceView

import datetime
import getpass
import json
import os
import re
import sys
import urllib

from text_stats import TextStats

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
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.main_window_delete)
        self.notebook = self.builder.get_object("notebook")

        # gtkwebkit
        browser_window = self.builder.get_object("browser_window")
        self.browser_view = WebKit2.WebView()
        self.browser_view.connect("load-changed", self.load_changed)
        browser_window.add(self.browser_view)

        self.location_entry.set_text("http://en.wikipedia.org/")
        self.location_entry_activate()
        self.browser_view.get_settings().set_property("enable-developer-extras",True)

        # gtksourceview
        lm = GtkSource.LanguageManager()
        self.editor_buffer = GtkSource.Buffer.new_with_language(lm.get_language("python"))
        self.filename = ""
        self.load_file("kad.py")
        self.editor_view = GtkSource.View.new_with_buffer(self.editor_buffer)
        self.editor_view.set_auto_indent(True)
        self.editor_view.set_show_line_numbers(True)
        self.editor_view.set_highlight_current_line(True)
        self.editor_view.set_insert_spaces_instead_of_tabs(True)
        self.editor_view.set_indent_width(4)
        self.editor_window = self.builder.get_object("editor_window")
        self.editor_window.add(self.editor_view)
        key, mod = Gtk.accelerator_parse("<Control>s")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.save_file)

        # save and reload KAD with Control-R
        key, mod = Gtk.accelerator_parse("<Control>r")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.reload_kad)

        # pdf viewer (Evince)
        path = self.file_uri_from_relative_path("pdf/deep_learning.pdf")
        EvinceDocument.init()
        self.pdf_document = EvinceDocument.Document.factory_get_document(path)
        self.pdf_view = EvinceView.View()
        self.pdf_model = EvinceView.DocumentModel()
        self.pdf_model.set_document(self.pdf_document)
        self.pdf_view.set_model(self.pdf_model)
        self.pdf_window = self.builder.get_object("pdf_window")
        self.pdf_window.add(self.pdf_view)

        self.jan_editor = self.builder.get_object("jan_editor")
        self.jan_editor_buffer = self.builder.get_object("jan_editor_buffer")
        self.visualizer_viewport = self.builder.get_object("visualizer_viewport")

        self.visualizer_view = WebKit2.WebView()
        self.visualizer_view.get_settings().set_enable_developer_extras(True)
        self.visualizer_viewport.add(self.visualizer_view)
        self.visualizer_view.get_context().get_security_manager().register_uri_scheme_as_cors_enabled("python")
        self.visualizer_view.get_context().register_uri_scheme("python", self.visualizer_request, None, None)

        window.fullscreen()
        window.show_all()

        self.jan_editor.hide()
        self.visualizer_viewport.hide()

    def file_uri_from_relative_path(self, path):
        return "file://" + os.path.abspath(path)

    def load_file(self, filename):
        filename = re.sub("file://", "", filename)
        if self.filename != "":
            self.ensure_saved()
        self.filename = filename
        try:
            with open(self.filename, 'r') as f:
                self.file_data = f.read()
        except IOError:
            self.file_data = ""
        self.editor_buffer.set_text(self.file_data)

    def load(self, uri):
        self.browser_view.load_uri(uri)

    def select_tab(self, tab):
        if tab == "web":
            index = 0
        elif tab == "edit":
            index = 1
        else:
            index = 2
        self.notebook.set_current_page(index)

    def get_tab(self):
        page = self.notebook.get_current_page()
        return self.get_tab_from_page(page)

    def get_tab_from_page(self, page):
        if page == 0:
            return "web"
        if page == 1:
            return "edit"
        if page == 2:
            return "pdf"

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
        os.execl("./kad.py", "./kad.py", self.get_tab())

    def main(self, args):
        if len(args) > 1:
            self.select_tab(args[1])
        Gtk.main()

    def visualizer_request(self, request, *args):
        value = eval("self." + request.get_path())

    def trigger_update(self, thing):
       self.js_function("update", {'test': "stuff", 'things': ['one', 2, {'name': "iii"}], "from_js": thing})

    def js_function(self, function, param):
        self.visualizer_view.run_javascript(function + "(" + json.dumps(param) + ")", None, None)

    def main_window_delete(self, *args):
        self.ensure_saved()
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
            tab = self.get_tab()
            filepath = ""
            if tab == "edit":
                filepath = self.file_uri_from_relative_path(self.filename)
            elif tab == "pdf":
                filepath = self.pdf_document.get_uri()

            if filepath != "":
                self.visualizer_view.load_uri(self.file_uri_from_relative_path("visualize.html"))
            self.visualizer_viewport.show()

    def location_entry_activate(self, *args):
        uri = self.location_entry.get_text()
        if "file://" in uri:
            if ".pdf" in uri:
                self.pdf_document = EvinceDocument.Document.factory_get_document(uri)
                self.pdf_model.set_document(self.pdf_document)
                self.select_tab("pdf")
            else:
                self.load_file(uri)
                self.select_tab("edit")
        else:
            if not("http" in uri):
                uri = "http://" + uri
            self.load(uri)
            self.select_tab("web")

    def load_changed(self, *args):
        if args[1] == WebKit2.LoadEvent.FINISHED and self.get_tab() == "web":
            uri = self.browser_view.get_uri()
            visualization_uri = "http://www.infocaptor.com/bubble-my-page?url=" + \
                                urllib.quote_plus(uri) + "&size=400"
            self.location_entry.set_text(uri)
            self.visualizer_view.load_uri(visualization_uri)

    def notebook_page_changed(self, notebook, page, page_num, *args):
        tab = self.get_tab_from_page(page_num)
        if tab == "web":
            location = self.browser_view.get_uri()
        elif tab == "edit":
            location = self.file_uri_from_relative_path(self.filename)
        else:
            location = self.pdf_document.get_uri()
        self.location_entry.set_text(location)


kad = KAD()
kad.main(sys.argv)
