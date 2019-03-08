import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import multiprocessing
from multiprocessing import Process
import time

def timeoutProcess():
    i=0
    while True:
        i += 1
        #print(i)
        time.sleep(1)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class SimpleWebSocket(tornado.websocket.WebSocketHandler):
    connections = set()
    users = []
    uid = ''
    current_question = 0
    answers = {1: {},
               2: {},
               3: {},
               4: {}}
    questions = {1: {'question': 'question 1','answers': ['A1', 'A2342342', 'A3', 'A4']},
        2: {'question': 'question 2', 'answers': ['A1', 'A2342342', 'A3', 'A4']},
        3: {'question': 'question 3', 'answers': ['A1', 'A2342342', 'A3', 'A4']},
        4: {'question': 'question 4', 'answers': ['A1', 'A2342342', 'A3', 'A4']}
                 }

    def open(self, user):
        self.uid = user
        self.connections.add(self)

    def on_message(self, message):
        for client in self.connections:
            res = json.loads(message)
            if("type" in res):
                if res["type"] == "open":

                    if res['user'] not in self.users and type(res['user']) is not list:
                        self.users.append(res['user'])
                        res['user'] = self.users

                if res["type"] == 'question':
                    self.play_game(res, client)

                if res['type'] == 'answer_quest':
                    # TODO: Multiprocessing Problem
                    # save all answers of all player
                    self.answers[self.current_question][self.uid] = res['id']

            message = json.dumps(res)
                #change to dashboard leter

            print(message)
            client.write_message(message)

    def play_game(self, res, client):
        # loop questions
        for i, q in self.questions.items():

            res['question'] = q['question']
            res['answers'] = q['answers']
            message = json.dumps(res)
            self.current_question = i
            print(message)
            client.write_message(message)
            taction = Process(target=timeoutProcess)
            taction.daemon = True;
            taction.start()
            taction.join(timeout=10)
            taction.terminate()


    def on_close(self):
        self.users.remove(self.uid)
        self.connections.remove(self)

        for client in self.connections:
            res = {}
            res['type'] = "close"
            res['user'] = self.users
            client.write_message(json.dumps(res))

        print('connection lost!!!')

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/websocket", SimpleWebSocket),
        (r"/websocket/username/(.*)", SimpleWebSocket)
    ])

if __name__ == "__main__":
    queue = multiprocessing.Queue()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()