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
import re
import urllib
import uuid

class UI:
    def __init__ (self, kad, file):
        self.kad= kad
        self.builder = Gtk.Builder()
        self.builder.add_from_file(file)
        self.builder.connect_signals(self)

    def main(self):
        Gtk.main()

    def set_language_from_filename(self, filename):
        lm = GtkSource.LanguageManager()
        language = lm.guess_language(filename)
        self.editor_buffer.set_language(language)

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

    def get_editor_text(self):
        start_iter = self.editor_buffer.get_start_iter()
        end_iter = self.editor_buffer.get_end_iter()
        return self.editor_buffer.get_text(start_iter, end_iter, True)

    def prepare(self):
        self.window = self.builder.get_object("main_window")
        self.location_entry = self.builder.get_object("location_entry")

        accelerators = Gtk.AccelGroup()
        self.window.add_accel_group(accelerators)
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
        self.editor_buffer = GtkSource.Buffer()
        self.kad.load_file("kad.py")
        self.editor_view = GtkSource.View.new_with_buffer(self.editor_buffer)
        self.editor_view.set_auto_indent(True)
        self.editor_view.set_show_line_numbers(True)
        self.editor_view.set_highlight_current_line(True)
        self.editor_view.set_insert_spaces_instead_of_tabs(True)
        self.editor_view.set_indent_width(4)
        self.editor_window = self.builder.get_object("editor_window")
        self.editor_window.add(self.editor_view)
        key, mod = Gtk.accelerator_parse("<Control>s")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.kad.save_file)

        # save and reload KAD with Control-R
        key, mod = Gtk.accelerator_parse("<Control>r")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.kad.reload_kad)

        # pdf viewer (Evince)
        path = self.kad.file_uri_from_relative_path("pdf/deep_learning.pdf")
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
        self.visualizer_view.get_context().register_uri_scheme("python", self.kad.visualizer_request, None, None)

        self.window.maximize()
        self.window.show_all()

        self.jan_editor.hide()
        self.visualizer_viewport.hide()

    # begin signal handlers

    def main_window_delete(self, *args):
        self.window.hide()
        self.kad.shutdown()
        Gtk.main_quit(*args)

    def save_button_clicked(self, *args):
        if self.jan_editor.is_visible():
            self.jan_editor.hide()
        else:
            # write JAN based on current location
            # TODO: detect existing, networked JAN and display it instead
            uri = self.location_entry.get_text()
            tab = self.get_tab()
            type = "url"
            if tab != "web":
                type = re.sub("[^.]*\.(.*)", "\g<1>", uri)
            time = str(datetime.datetime.now())
            user = getpass.getuser()
            jan = {
                'type': type,
                'link': uri,
                'uuid': str(uuid.uuid5(uuid.NAMESPACE_URL, uri)),
                'metadata': [
                    {
                        'name': 'retrieval time',
                        'value': time
                    },
                    {
                        'name': 'originating user',
                        'value': user
                    }
                ]}
            if tab == "web":
                jan["metadata"].append({
                        'name': "page title",
                        'value': self.browser_view.get_title()
                    })
            self.jan_editor_buffer.set_text(json.dumps(jan, indent=4))
            self.jan_editor.show()
            self.add_jan(jan)

    def add_jan(self, jan):
        with open("new_jan/" + jan["uuid"] + ".jan", 'w') as f:
            f.write(json.dumps(jan))

    def visualize_button_clicked(self, *args):
        if self.visualizer_viewport.is_visible():
            self.visualizer_viewport.hide()
        else:
            tab = self.get_tab()
            filepath = ""
            if tab == "edit":
                filepath = self.kad.current_uri()
            elif tab == "pdf":
                filepath = self.pdf_document.get_uri()

            if filepath != "":
                self.visualizer_view.load_uri(self.kad.file_uri_from_relative_path("visualize.html"))
            self.visualizer_viewport.show()

    def location_entry_activate(self, *args):
        uri = self.location_entry.get_text()
        if "file://" in uri:
            if ".pdf" in uri:
                self.pdf_document = EvinceDocument.Document.factory_get_document(uri)
                self.pdf_model.set_document(self.pdf_document)
                self.select_tab("pdf")
            else:
                self.kad.load_file(uri)
                self.select_tab("edit")
        else:
            if not("http" in uri):
                uri = "http://" + uri
            self.kad.load(uri)
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
            location = self.kad.current_uri()
        else:
            location = self.pdf_document.get_uri()
        self.location_entry.set_text(location)