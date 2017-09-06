
class JobInterruptedException(Exception):
    def __init__(self, *args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class RequestFailedException(Exception):
    def __init__(self, error_msg, *args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
        self.error_msg = error_msg