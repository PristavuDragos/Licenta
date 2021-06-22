from threading import Thread
from Server.Database import meeting_session_collection
from Server.Database import uploaded_solution_collection


class FileServerThread(Thread):
    def __init__(self, ip, port, conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn

    def run(self):
        try:
            msg = self.conn.recv(1024).decode().split("\/")
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
                uploaded_solution_collection.insert_solution([session_code, username, file])
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
                result = uploaded_solution_collection.get_solution_count_of_session([session_code])
                if result is not None:
                    for count in range(result):
                        entry_to_get = count + 1
                        solution = uploaded_solution_collection.get_solution([session_code, entry_to_get])
                        response = self.conn.recv(1024).decode()
                        if response == "Next":
                            if solution[0] == 1:
                                file = solution[2]
                                username = solution[1]
                            else:
                                file = b""
                                username = "error"
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
