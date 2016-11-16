class Config:
    current_janbase = 'default'
    listeners = []

    @classmethod
    def set_current_janbase(klass, janbase):
        klass.current_janbase = janbase
        for listener in klass.listeners:
            listener()