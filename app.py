import tornado.ioloop
import tornado.web
import tornado.websocket
from datetime import datetime
from tornado.escape import json_encode
import json

ELASTIC_INDEX = "simple-chat-tornado"

ROOMS = {}

dtjson = lambda obj: (
    obj.isoformat() if isinstance(obj, datetime) else None
)

class StaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

class IndexHandler(tornado.web.RequestHandler):
    def get(request):
        with open('index.html') as f:
            request.write(f.read())

class RoomSocket(tornado.websocket.WebSocketHandler):
    def open(self, room_id):
        self.room_id = room_id
        if not room_id in ROOMS:
            ROOMS[room_id] = []
        ROOMS[room_id].append(self)

    def on_close(self):
        ROOMS[self.room_id].remove(self)
        if len(ROOMS[self.room_id]) is 0:
            ROOMS.pop(self.room_id, None)

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/assets/(.*)', StaticFileHandler, {'path': 'bower_components'}),
    (r'/styles/(.*)', StaticFileHandler, {'path': 'styles'}),
    (r'/scripts/(.*)', StaticFileHandler, {'path': 'scripts'}),
    (r'/angular_templates/(.*)', StaticFileHandler, {'path': 'angular_templates'}),
    (r'/roomsocket/(.*)', RoomSocket)
])
app.listen(8888)
tornado.ioloop.IOLoop.instance().start()
