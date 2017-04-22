from tornado import websocket
from redis import StrictRedis

redis_client = StrictRedis(db=1)


class ChatSocketHandler(websocket.WebSocketHandler):

    waiters = set()

    def open(self, *args, **kwargs):
        self.channel = kwargs.get('channel', 'main')
        self.waiters.add((self.channel, self))





    def on_message(self, message):
        pass

    def data_received(self, chunk):
        pass



