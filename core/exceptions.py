
class UploadException(Exception):
    def __init__(self, response):
        self.response = response

    def serialize(self):
        return self.response.serialize()
