from jan import JAN

class PDFWatcher:
    @staticmethod
    def new_file(path):
        jan = JAN.find_from_uri(path)
        if jan == None:
            jan = JAN.new_from_uri_and_type(path, "pdf")
            jan.add_new()
