import re
import socket
import pandas as pd


# Main event loop
def reactor(host, port):
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(5)
    print(f'Server started {host} {port}')

    try:
        while True:
            conn, cli_address = sock.accept()
            process_request(conn, cli_address)
    except:
        print(f'Error {cli_address}')
    finally:
        sock.close()


def process_request(conn, cli_address):
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

                if line == 'data':
                    conn.sendall(b'please input data\r\n')
                    mode = 'data'
                    continue

                print(f'{cli_address} --> {line}')
                regex = r'^\d{4}\s\b\w{2}\b\s\d{2}:\d{2}:\d{2}.\d{3}\s\d{2}$'
                try:
                    if re.match(regex, line) is not None:
                        data = line
                    else:
                        conn.sendall(b'Error: data does not match format\r\n')
                except ValueError:
                    conn.sendall(b'Error: failed to validate format\r\n')
                    continue

                if mode == 'data':
                    matches = re.finditer(regex, data)
                    for matchNum, match in enumerate(matches):
                        list_input_data = match.group().split(' ')
                        conn.sendall(b'input data: %a\r\n' % match.group())
                        if list_input_data[3] == '00':
                            print(
                                f"Cпортсмен, нагрудный номер {list_input_data[0]} прошёл отсечку {list_input_data[1]} в "
                                f"{list_input_data[2][0:-2]}")
                        # write_file(list_input_data)
    finally:
        print(f'{cli_address} quit')
        file.close()
        conn.close()


def write_file(data):
    df = pd.DataFrame({
        'Номер участника': [data[0]],
        'id канала': [data[1]],
        'Время': [data[2]],
        'Номер группы': [data[3]]
    })
    df.to_excel('base.xlsx')


if __name__ == '__main__':
    reactor('localhost', 8080)
