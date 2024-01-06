import os
import socket

QUEUE_LEN = 10
IP = '0.0.0.0'
PORT = 80
END_LINE = '\r\n'
SOCKET_TIMEOUT = 2
VALID_VERBS = ['GET']
HTTP_VERSION = 'HTTP/1.1'
WEB_ROOT = 'webroot'
SPECIAL_URIS = {'/moved': 302, '/forbidden': 403, '/error': 500}
DEFAULT_PATH = '/index.html'
STATUS_MSG = {
    200: 'OK', 302: 'MOVED TEMPORARILY', 400: 'BAD REQUEST', 404: 'NOT FOUND',
    500: 'INTERNAL SERVER ERROR', 403: 'FORBIDDEN'
}
TYPES = {
    'html': 'text/html;charset=utf-8', 'jpg': 'image/jpeg', 'css': 'text/css', 'js': 'text/javascript;charset=utf-8',
    'txt': 'text/plain', 'ico': 'image/x-icon', 'gif': 'image/jpeg', 'png': 'image/png'
}
NOT_FOUND_FILE = 'not-found.html'


def send_response(client_socket, response):
    while response:
        size = client_socket.send(response)
        response = response[size:]


def receive_line(client_socket):
    data = ''
    while not data.endswith(END_LINE):
        data += client_socket.recv(1).decode()
    return data


def receive_http_request(client_socket):
    current_line = ''
    lines = []
    while current_line != END_LINE:
        current_line = receive_line(client_socket)
        lines.append(current_line)
    # remove \r\n from the final result
    return [line[:-len(END_LINE)] for line in lines]


def validate_request(client_socket):
    request = receive_http_request(client_socket)
    request_line = request[0].split(' ')
    if len(request_line) != 3 or request_line[2] != HTTP_VERSION or request_line[0] not in VALID_VERBS:
        return False, ''
    return True, request_line[1]


def get_file_path(uri):
    if uri == '/' or uri == '':
        return WEB_ROOT + DEFAULT_PATH
    return WEB_ROOT + uri


def get_status_code(is_valid, uri):
    file_path = get_file_path(uri)
    if not is_valid:
        return 400
    elif uri in SPECIAL_URIS.keys():
        return SPECIAL_URIS[uri]
    elif not os.path.isfile(file_path):
        return 404
    return 200


def read_file(path):
    with open(path, 'rb') as f:
        data = f.read()
    return data


def build_header(key, value):
    return f'{key}: {value}\r\n'.encode()


def handle_client(client_socket):
    is_valid, uri = validate_request(client_socket)
    status_code = get_status_code(is_valid, uri)
    body = b''

    response = f'{HTTP_VERSION} {status_code} {STATUS_MSG[status_code]}\r\n'.encode()

    if status_code == 302:
        response += build_header('Location', '/')
    elif status_code == 200 or status_code == 404:
        if status_code == 200:
            file_path = get_file_path(uri)
        else:
            file_path = NOT_FOUND_FILE

        body = read_file(file_path)
        response += build_header('Content-Length', len(body))
        response += build_header('Content-Type', TYPES[file_path.split('.')[-1]])

    response += '\r\n'.encode()
    response += body

    send_response(client_socket, response)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_LEN)
        while True:
            client_socket, client_addr = server_socket.accept()
            try:
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print(f'client socket error: {str(err)}')
            finally:
                client_socket.close()
    except socket.error as err:
        print(f'server socket error: {str(err)}')
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
