import socket

QUEUE_LEN = 10
IP = '0.0.0.0'
PORT = 80
END_LINE = '\r\n'
SOCKET_TIMEOUT = 2
VALID_VERBS = ['GET']
HTTP_VERSION = 'HTTP/1.1'
WEB_ROOT = 'webroot'


def build_response(status_code, body=None, content_type=None):
    pass


def process_request(uri):
    pass


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


def handle_client(client_socket):
    is_valid, uri = validate_request(client_socket)
    if not is_valid:
        response = build_response(400)
    else:
        status_code, body, content_type = process_request(uri)
        response = build_response(status_code, body, content_type)

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
