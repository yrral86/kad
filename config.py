class Config:
    current_janbase = 'default'
    listeners = []

    @classmethod
    def set_current_janbase(klass, janbase):
        klass.current_janbase = janbase
        for listener in klass.listeners:
            listener()

    @classmethod
    def current_janbase_dir(klass):
        return "data/" + klass.current_janbase + "/"