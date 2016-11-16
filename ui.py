import gi
from gi.repository import GLib
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

import hashlib
import re
import os
import uuid

from visual import V
from file_utils import F
from jan import JAN
from webcawler import *
from webcawler2 import *
class UI:
    def __init__ (self, kad, file):
        self.kad= kad
        self.builder = Gtk.Builder()
        self.builder.add_from_file(file)
        self.builder.connect_signals(self)
        self.V = V(self)

    def main(self):
        Gtk.main()

    def set_language_from_filename(self, filename):
        lm = GtkSource.LanguageManager()
        language = lm.guess_language(filename)
        self.editor_buffer.set_language(language)

    def get_editor_text(self):
        start_iter = self.editor_buffer.get_start_iter()
        end_iter = self.editor_buffer.get_end_iter()
        return self.editor_buffer.get_text(start_iter, end_iter, True)

    def get_jan_editor_text(self):
        start_iter = self.jan_editor_buffer.get_start_iter()
        end_iter = self.jan_editor_buffer.get_end_iter()
        return self.jan_editor_buffer.get_text(start_iter, end_iter, True)


    def prepare(self):
        self.window = self.builder.get_object("main_window")
        self.editor_location_entry = self.builder.get_object("editor_location_entry")
        self.knowledge_location_entry = self.builder.get_object("knowledge_location_entry")
        self.save_jan_button = self.builder.get_object("save_jan_button")

        accelerators = Gtk.AccelGroup()
        self.window.add_accel_group(accelerators)
        key, mod = Gtk.accelerator_parse("<Control>l")
        self.knowledge_location_entry.add_accelerator("grab-focus", accelerators, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>q")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.main_window_delete)

        # gtkwebkit
        self.browser_window = self.builder.get_object("browser_window")
        self.browser_view = WebKit2.WebView()
        self.browser_view.connect("load-changed", self.load_changed)
        self.browser_view.connect("decide-policy", self.decide_policy)
        self.browser_view.get_context().connect("download-started", self.download_started)
        self.browser_view.get_settings().set_property("enable-developer-extras",True)
        self.browser_window.add(self.browser_view)

        # gtksourceview
        self.editor_buffer = GtkSource.Buffer()
        self.open_uri(F.uri_from_path("example_tex/paper.tex"))
        self.editor_view = GtkSource.View.new_with_buffer(self.editor_buffer)
        self.editor_view.set_auto_indent(True)
        self.editor_view.set_show_line_numbers(True)
        self.editor_view.set_highlight_current_line(True)
        self.editor_view.set_insert_spaces_instead_of_tabs(True)
        self.editor_view.set_indent_width(4)
        self.editor_window = self.builder.get_object("editor_window")
        self.editor_window.add(self.editor_view)
        key, mod = Gtk.accelerator_parse("<Control>s")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.save_editor_button_clicked)

        # save and reload KAD with Control-R
        key, mod = Gtk.accelerator_parse("<Control>r")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.kad.reload_kad)

        # pdf viewer (Evince)
        self.pdf_window = self.builder.get_object("pdf_window")
        EvinceDocument.init()
        self.pdf_view = EvinceView.View()
        self.pdf_model = EvinceView.DocumentModel()
        self.pdf_view.set_model(self.pdf_model)
        self.pdf_window.add(self.pdf_view)

        self.jan_scroll_window = self.builder.get_object("jan_scroll_window")
        self.jan_editor_buffer = self.builder.get_object("jan_editor_buffer")
        self.visualizer_viewport = self.builder.get_object("visualizer_viewport")

        self.visualizer_view = WebKit2.WebView()
        self.visualizer_view.get_settings().set_enable_developer_extras(True)
        self.visualizer_viewport.add(self.visualizer_view)
        self.visualizer_view.get_context().get_security_manager().register_uri_scheme_as_cors_enabled("python")
        self.visualizer_view.get_context().register_uri_scheme("python", self.V.visualizer_request, None, None)
        self.visualizer_view.load_uri(F.uri_from_path("visualize.html"))

        # file open dialog
        key, mod = Gtk.accelerator_parse("<Control>o")
        Gtk.AccelGroup.connect(accelerators, key, mod, Gtk.AccelFlags.VISIBLE, self.open_editor_button_clicked)

        self.window.maximize()
        self.window.show_all()

        self.jan_scroll_window.hide()
        self.open_uri("http://scholar.google.com/")

        self.cbox = self.builder.get_object("janbase_selection_box")
        self.model = Gtk.ListStore(str)
        self.cbox.set_model(self.model)        
        self.cell = Gtk.CellRendererText()
        self.cbox.pack_start(self.cell, False)
        self.cbox.add_attribute(self.cell, 'text',0)
        self.populate_selection_box()        

        self.cbox_janbase1 = self.builder.get_object("combo_box1_janbase")
        self.model1 = Gtk.ListStore(str)
        self.cbox_janbase1.set_model(self.model1)        
        self.cell1 = Gtk.CellRendererText()
        self.cbox_janbase1.pack_start(self.cell1, False)
        self.cbox_janbase1.add_attribute(self.cell1, 'text',0)
        
        self.cbox_janbase2 = self.builder.get_object("combo_box2_janbase")
        self.model2 = Gtk.ListStore(str)
        self.cbox_janbase2.set_model(self.model2)        
        self.cell2 = Gtk.CellRendererText()
        self.cbox_janbase2.pack_start(self.cell2, False)
        self.cbox_janbase2.add_attribute(self.cell2, 'text',0)
        
        
    def populate_selection_box(self):        
        self.cbox = self.builder.get_object("janbase_selection_box")
        self.model = self.cbox.get_model()
        self.model.clear()
        
        for janbases in self.kad.get_janbases():
            self.model.append([janbases])
            #print(janbases)
    
        
    def activate_pdf_view(self):
        self.browser_window.hide()
        self.pdf_window.show()

    def activate_web_view(self):
        self.pdf_window.hide()
        self.browser_window.show()

    def open_uri(self, uri):
        if not("http" in uri) and not("file:///" in uri):
            uri = F.uri_from_path(uri)
        if (".pdf" in uri) or ("http" in uri):
            self.knowledge_location_entry.set_text(uri)
            self.knowledge_location_entry_activate(True)
        else:
            self.editor_location_entry.set_text(uri)
            self.editor_location_entry_activate()

    # begin signal handlers

    def settings_button_clicked(self, *args):
	print 'OK1'
        self.settings_dialog = self.builder.get_object("settings_dialog")
        self.settings_dialog.run()

    def Search_button_clicked(self, *args):
	Keyword_entry = self.builder.get_object("Keyword_entry")
	keyword = Keyword_entry.get_text()
	Pagenum_entry = self.builder.get_object("Pagenum_entry")
	pagenum = Pagenum_entry.get_text()
	Year_entry = self.builder.get_object("Year_entry")
	year = Year_entry.get_text()
	webcawler(keyword,pagenum,year)

    def Search_button1_clicked(self, *args):
	Keyword_entry = self.builder.get_object("Keyword_entry")
	keyword = Keyword_entry.get_text()
	Pagenum_entry = self.builder.get_object("Pagenum_entry")
	pagenum = Pagenum_entry.get_text()
	Year_entry = self.builder.get_object("Year_entry")
	year = Year_entry.get_text()
	webcawler2(keyword,pagenum,year)

    def settings_save_button_clicked(self, *args):
        self.settings_dialog.hide()

    def render_button_clicked(self, *args):
        self.save_editor_button_clicked()
        print os.popen("cd example_tex; pdflatex paper").read()
        self.open_uri(F.uri_from_path("example_tex/paper.pdf"))

    def save_editor_button_clicked(self, *args):
        self.kad.save_file()

    def open_editor_button_clicked(self, *args):
        file_chooser = Gtk.FileChooserDialog("Open file", self.window,
                                             Gtk.FileChooserAction.OPEN,
                                             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                              Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = file_chooser.run()
        if response == Gtk.ResponseType.OK:
            self.open_uri(file_chooser.get_filename())
        file_chooser.destroy()

    def decide_policy(self, view, decision, type):
        uri = decision.get_request().get_uri()
        if re.match(".*\.pdf$", uri, re.IGNORECASE):
            decision.download()

    def download_started(self, context, download):
        # download to random file
        uri = F.uri_from_path("pdf/" + str(uuid.uuid4()) + ".pdf")
        download.set_destination(uri)
        download.connect("finished", self.download_finished)

    def download_finished(self, download):
        response = download.get_response();
        status = download.get_response().get_status_code()
        if status == 200:
            uri = download.get_destination()
            # rename file based on contents to avoid duplicate PDFs
            contents = F.slurp(uri)
            new_filename = hashlib.sha256(contents).hexdigest()
            old_uri = uri
            uri = F.uri_from_path("pdf/" + new_filename + ".pdf")
            F.mv(old_uri, uri)
            self.open_uri(uri)
            # create the JAN
            jan = JAN.new_from_uri_and_type(uri, None)
            jan.add_new()

    def main_window_delete(self, *args):
        self.kad.shutdown()
        Gtk.main_quit(*args)

    def reload_jan(self):
        uri = self.editor_location_entry.get_text();
        jan = JAN.find_from_uri(uri)
        if jan != None:
            new_json = jan.to_pretty_json(4)
            old_json = self.get_jan_editor_text()
            if new_json != old_json:
                self.jan_editor_buffer.set_text(jan.to_pretty_json(4))
        return self.jan_reloading

    def editor_location_entry_activate(self, *args):
        uri = self.editor_location_entry.get_text()
        self.kad.load_file(uri)

    def knowledge_location_entry_activate(self, *args):
        uri = self.knowledge_location_entry.get_text()
        if ("file://" in uri) and (".pdf" in uri):
            self.pdf_document = EvinceDocument.Document.factory_get_document(uri)
            self.pdf_model.set_document(self.pdf_document)
            self.activate_pdf_view()
        else:
            if not("http" in uri):
                uri = "http://" + uri
            self.activate_web_view()
            if args[0]:
                self.kad.load(uri)
        if JAN.find_from_uri(uri) == None:
            self.save_jan_button.show()
        else:
            self.save_jan_button.hide()

    def load_changed(self, *args):
        if args[1] == WebKit2.LoadEvent.FINISHED:
            uri = self.browser_view.get_uri()
            self.knowledge_location_entry.set_text(uri)
            self.knowledge_location_entry_activate(False)
    
    def merge_janbase_clicked(self, *args):
        self.builder.get_object("janbase_reusable_dialog").show()
        self.builder.get_object("combo_box1_label").show()
        self.builder.get_object("combo_box2_label").show()
        self.builder.get_object("combo_box1_janbase").show()
        self.builder.get_object("combo_box2_janbase").show()
        self.builder.get_object("text_box1_label").hide()
        self.builder.get_object("text_box1").hide()
        self.builder.get_object("combo_box1_label").set_label("Merge")
        self.builder.get_object("combo_box2_label").set_label("into")
        
        self.cbox = self.builder.get_object("combo_box1_janbase")
        self.model = self.cbox.get_model()
        self.model.clear()
        self.cbox2 = self.builder.get_object("combo_box2_janbase")
        self.model2 = self.cbox2.get_model()
        self.model2.clear()
        for janbases in self.kad.get_janbases():
            self.model.append([janbases])        
            self.model2.append([janbases])
            
        self.builder.get_object("combo_box_action_label").set_label("Merge Janbases")
        action_button = self.builder.get_object("janbase_action_button")
        action_button.set_label("merge")
        action_button.connect("clicked",self.merge_janbase,None)
        
    def merge_janbase(self,*args):
        janbase_merge_target = self.builder.get_object("combo_box1_janbase").get_active()
        janbase_to_merge = self.builder.get_object("combo_box2_janbase").get_active()
        janbase_model_target = self.builder.get_object("combo_box1_janbase").get_model()
        janbase_model_tomerge = self.builder.get_object("combo_box2_janbase").get_model()        
        if janbase_merge_target == janbase_to_merge or janbase_merge_target == "" or janbase_to_merge =="":
            pass #error message
        else:
            self.kad.merge_janbases(janbase_model_target[janbase_merge_target],janbase_model_tomerge[janbase_to_merge])
            self.builder.get_object("janbase_reusable_dialog").hide()
            
    def create_janbase(self, *args):
        if self.builder.get_object("text_box1").get_text() != "":
            self.kad.create_janbase(self.builder.get_object("text_box1").get_text())  
            self.builder.get_object("janbase_reusable_dialog").hide()    
            self.populate_selection_box()
            
    def create_janbase_clicked(self,*args):
        #create janbase
        self.builder.get_object("janbase_reusable_dialog").show()
        self.builder.get_object("combo_box1_label").hide()
        self.builder.get_object("combo_box2_label").hide()
        self.builder.get_object("combo_box1_janbase").hide()
        self.builder.get_object("combo_box2_janbase").hide()
        self.builder.get_object("text_box1_label").set_label("Enter new Janbase name")
        self.builder.get_object("text_box1").set_text("")
        self.builder.get_object("combo_box_action_label").set_label("Create New Janbase")
        action_button = self.builder.get_object("janbase_action_button")
        action_button.set_label("create")
        action_button.connect("clicked",self.create_janbase,None)
        
    def load_janbase(self,*args):
        if self.builder.get_object("combo_box1_janbase").get_active() != "":
            model = self.builder.get_object("combo_box1_janbase").get_model()
            index = self.builder.get_object("combo_box1_janbase").get_active()
            self.kad.load_janbase(model[index][0])
            self.builder.get_object("janbase_reusable_dialog").hide()
        
    def load_janbase_clicked(self, *args):
        self.builder.get_object("janbase_reusable_dialog").show()
        self.builder.get_object("combo_box1_label").show()
        self.builder.get_object("combo_box2_label").hide()
        self.builder.get_object("combo_box1_janbase").show()
        self.builder.get_object("combo_box2_janbase").hide()
        self.builder.get_object("text_box1_label").hide()
        self.builder.get_object("text_box1").hide()
        self.builder.get_object("combo_box1_label").set_label("Select Janbase")
        self.builder.get_object("combo_box_action_label").set_label("Load Janbase")
        action_button = self.builder.get_object("janbase_action_button")
        action_button.set_label("load")
        action_button.connect("clicked",self.load_janbase,None)
        janbase_list = self.builder.get_object("combo_box1_janbase").get_model()
        janbase_list.clear()
        for janbases in self.kad.get_janbases():
            janbase_list.append([janbases])
        janbase_list.active = 0
        
    def delete_janbase_clicked(self, *args):
        pass
    def janbase_selection_box_changed(self, *args):
        pass
    def settings_cancel_button_clicked(self, *args):
        self.settings_dialog.hide()
            
    def save_jan_button_clicked(self, *args):
        uri = self.knowledge_location_entry.get_text()
        # detect existing JAN
        jan = JAN.find_from_uri(uri)
        if jan == None:
            # JAN not found, write a new JAN
            janType = None
            if "http" in uri:
                janType = "url"
            jan = JAN.new_from_uri_and_type(uri, janType)
            if "http" in uri:
                jan.add_metadata('page title', self.browser_view.get_title())
            jan.add_new()
            self.knowledge_location_entry_activate(False)
    def janbase_cancel_button_clicked(self, *args):
        self.builder.get_object("janbase_reusable_dialog").hide()
