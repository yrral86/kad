import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

builder = Gtk.Builder()
builder.add_from_file("shell.glade")

window = builder.get_object("mainWindow")
browserWindow = builder.get_object("browserWindow")

browserView = WebKit2.WebView()
browserWindow.add(browserView)

window.show_all()
browserView.open("http://www.google.com")

Gtk.main()
