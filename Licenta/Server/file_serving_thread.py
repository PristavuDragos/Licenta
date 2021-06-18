from threading import Thread
from Server.Database import meeting_session_collection
from Utils import functions


class FileServerThread(Thread):
    def __init__(self, ip, port, conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn

    def run(self):
        try:
            msg = self.conn.recv(1024).decode().split("\/")
            print(msg)
            if msg[0] == "UploadTest":
                session_code = msg[1]
                self.conn.send("Start".encode("utf-8"))
                file = b""
                while True:
                    data = self.conn.recv(1024)
                    if not data:
                        break
                    else:
                        file += data
                meeting_session_collection.set_session_subject([session_code, file])
            elif msg[0] == "UploadSolution":
                session_code = msg[1]
                username = msg[2]
                self.conn.send("Start".encode("utf-8"))
                file = b""
                while True:
                    data = self.conn.recv(1024)
                    if not data:
                        break
                    else:
                        file += data
                meeting_session_collection.add_session_solution([session_code, file, username])
            elif msg[0] == "DownloadSubject":
                session_code = msg[1]
                self.conn.send("Proceed".encode("utf-8"))
                response = self.conn.recv(1024).decode()
                if response == "Start":
                    result = meeting_session_collection.get_session_subject([session_code])
                    if result[0]:
                        file = result[1]
                        it = 1
                        while it * 1024 < len(file):
                            self.conn.send(file[(it - 1) * 1024: it * 1024])
                            it += 1
                        else:
                            self.conn.send(file[(it - 1) * 1024: len(file)])
                            self.conn.send("Done".encode("utf-8"))
            elif msg[0] == "DownloadSolutions":
                session_code = msg[1]
                self.conn.send("Proceed".encode("utf-8"))
                result = meeting_session_collection.get_session_solutions([session_code])
                solution_array = result[1]
                if result[0]:
                    for solution in solution_array:
                        response = self.conn.recv(1024).decode()
                        if response == "Next":
                            file = solution[1]
                            username = solution[0]
                            self.conn.send(username.encode("utf-8"))
                            response = self.conn.recv(1024).decode()
                            if response == "Start":
                                it = 1
                                while it * 1024 < len(file):
                                    self.conn.send(file[(it - 1) * 1024: it * 1024])
                                    it += 1
                                else:
                                    self.conn.send(file[(it - 1) * 1024: len(file)])
                                    self.conn.send("Done".encode("utf-8"))
                    else:
                        self.conn.send("End".encode("utf-8"))
        except Exception as err:
            print(err)
