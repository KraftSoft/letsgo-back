
class UploadException(Exception):
    def __init__(self, response):
        self.response = response
