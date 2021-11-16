import re
import socket


class Sratr_server:
    def __init__(self):
        self.regex = r'^\d{4}\s\b\w{2}\b\s\d{2}:\d{2}:\d{2}.\d{3}\s\d{2}$'

    def reactor(self, host, port):
        sock = socket.socket()
        sock.bind((host, port))
        sock.listen(5)
        print(f'Server started {host} {port}')

        try:
            while True:
                conn, cli_address = sock.accept()
                self.process_request(conn, cli_address)
        except:
            print(f'Error {cli_address}')
        finally:
            sock.close()

    def process_request(self, conn, cli_address):
        data = ''
        file = conn.makefile()

        print(f'Received a connection from {cli_address}')
        mode = 'data'
        try:
            conn.sendall(b'welcome: commands for work:\r\n'
                         b'quit - disconnect commands\r\n'
                         b'data - command for data transfer(default)\r\n')
            conn.sendall(b'Attention: data entry format - BBBB NN HH:MM:SS.zhq GG\r\n')
            while True:
                line = file.readline()
                if line:
                    line = line.rstrip()
                    if line == 'quit':
                        conn.sendall(b'connection closed\r\n')
                        return

                    print(f'{cli_address} --> {line}')

                    try:
                        if re.match(self.regex, line) is not None:
                            data = line
                        else:
                            conn.sendall(b'Error: data does not match format\r\n')
                    except ValueError:
                        conn.sendall(b'Error: failed to validate format\r\n')
                        continue

                    if mode == 'data':
                        matches = re.finditer(self.regex, data)
                        for matchNum, match in enumerate(matches):
                            list_input_data = match.group().split(' ')
                            conn.sendall(b'input data: %a\r\n' % match.group())
                            if list_input_data[3] == '00':
                                print(
                                    f"Cпортсмен, нагрудный номер {list_input_data[0]} прошёл отсечку {list_input_data[1]} в "
                                    f"{list_input_data[2][0:-2]}")
                            self.write_file(match.group())
        finally:
            print(f'{cli_address} quit')
            file.close()
            conn.close()

    def write_file(self, data):
        try:
            with open('file.txt', mode='a+') as f:
                f.write(data + '\r')
            f.close()
        except:
            print('writing data to file failed')


if __name__ == '__main__':
    run = Sratr_server()
    run.reactor('localhost', 8080)
