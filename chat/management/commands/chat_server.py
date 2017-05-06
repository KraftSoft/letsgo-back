import datetime
import signal

from django.core.management import BaseCommand
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from chat.tornado import application


class Command(BaseCommand):
    def sig_handler(self, sig, frame):
        """Catch signal and init callback"""
        IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        """Stop server and add callback to stop i/o loop"""
        self.http_server.stop()

        io_loop = IOLoop.instance()
        io_loop.add_timeout(datetime.timedelta(seconds=600), io_loop.stop)

    def handle(self, *args, **options):
        self.http_server = HTTPServer(application)
        self.http_server.listen(9000, address="127.0.0.1")

        # Init signals handler
        signal.signal(signal.SIGTERM, self.sig_handler)

        # This will also catch KeyboardInterrupt exception
        signal.signal(signal.SIGINT, self.sig_handler)

        IOLoop.instance().start()
