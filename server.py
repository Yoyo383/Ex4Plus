"""
Author: Yoad Winter
Date: 6.1.2024
Description: A very basic HTTP server.
"""
import os
import socket
import logging


LOG_FORMAT = '[%(levelname)s | %(asctime)s | %(processName)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'

QUEUE_LEN = 10
IP = '0.0.0.0'
PORT = 80
END_LINE = '\r\n'
HEADER_KEY_VALUE_SEP = ': '
PARAMETER_SEP = '&'
PARAM_KEY_VALUE_SEP = '='
PARAMETER_BEGIN = '?'
SOCKET_TIMEOUT = 2
VALID_VERBS = ['GET', 'POST']
HTTP_VERSION = 'HTTP/1.1'
WEB_ROOT = 'webroot'
SPECIAL_URIS = {'/moved': 302, '/forbidden': 403, '/error': 500}
DEFAULT_PATH = '/index.html'
STATUS_MSG = {
    200: 'OK', 302: 'MOVED TEMPORARILY', 400: 'BAD REQUEST', 404: 'NOT FOUND',
    500: 'INTERNAL SERVER ERROR', 403: 'FORBIDDEN'
}
TYPES = {
    '.html': 'text/html;charset=utf-8', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.css': 'text/css',
    '.js': 'text/javascript;charset=utf-8', '.txt': 'text/plain', '.ico': 'image/x-icon', '.gif': 'image/jpeg',
    '.png': 'image/png'
}
NOT_FOUND_FILE = 'not-found.html'
UPLOAD_DIR = 'upload'


def send_response(client_socket, response):
    """
    Sends a response through the socket.
    :param client_socket: The socket.
    :type client_socket: socket.socket
    :param response: The response to send.
    :type response: bytes
    :return: None.
    """
    while response:
        size = client_socket.send(response)
        response = response[size:]


def receive_line(client_socket):
    """
    Receive a single line of the request.
    :param client_socket: The socket.
    :type client_socket: socket.socket
    :return: The line received.
    :rtype: str
    """
    data = ''
    while not data.endswith(END_LINE):
        data += client_socket.recv(1).decode()
    return data


def parse_headers(lines):
    """

    :type lines: list[str]
    :return:
    """
    headers = {}
    for line in lines[1:-1]:
        key, value = line.split(HEADER_KEY_VALUE_SEP)
        headers[key.lower()] = value
    return headers


def receive_http_request(client_socket):
    """
    Receives the entire HTTP request.
    :param client_socket: The socket.
    :type client_socket: socket.socket
    :return: The HTTP request as a list of its lines.
    :rtype: list[str]
    """
    current_line = ''
    lines = []
    while current_line != END_LINE:
        current_line = receive_line(client_socket)
        lines.append(current_line)
    # remove \r\n from the final result
    lines = [line[:-len(END_LINE)] for line in lines]
    headers = parse_headers(lines)
    body, body_type = None, None
    if 'content-length' in headers.keys() and 'content-type' in headers.keys():
        body = client_socket.recv(int(headers['content-length']))
        body_type = headers['content-type']
    return lines, body, body_type


def validate_request(request):
    """
    Checks if the request is valid.
    :param request: The HTTP request.
    :type request: list[str]
    :return: Whether the request is valid, the URI (if the request is not valid it returns an empty string), and the
    parameters as a dict.
    :rtype: tuple[bool, str, dict[str, str]]
    """
    # splits the request line
    request_line = request[0].split(' ')
    if len(request_line) != 3 or request_line[2] != HTTP_VERSION or request_line[0] not in VALID_VERBS:
        return False, None, None

    params = {}
    uri_params_list = request_line[1].split(PARAMETER_BEGIN)
    uri = uri_params_list[0]
    if len(uri_params_list) == 2:
        params_list = uri_params_list[1].split(PARAMETER_BEGIN)[-1].split(PARAMETER_SEP)
        for param in params_list:
            key, value = param.split(PARAM_KEY_VALUE_SEP)
            params[key] = value

    return True, uri, params


def get_file_path(uri):
    """
    Returns the filepath for a URI.
    :param uri: The URI.
    :type uri: str
    :return: The filepath for the URI.
    :rtype: str
    """
    if uri == '/' or uri == '':
        return WEB_ROOT + DEFAULT_PATH
    return WEB_ROOT + uri


def get_status_code(is_valid, uri):
    """
    Returns the status code of the request.
    :param is_valid: Is the request valid.
    :type is_valid: bool
    :param uri: The URI of the request.
    :type uri: str
    :return: The status code.
    :rtype: int
    """
    file_path = get_file_path(uri)
    if not is_valid:
        return 400
    elif uri in SPECIAL_URIS.keys():
        return SPECIAL_URIS[uri]
    elif not os.path.isfile(file_path):
        return 404
    return 200


def read_file(path):
    """
    Reads a file and returns its bytes.
    :param path: The file path.
    :type path: str
    :return: The file's content as bytes.
    :rtype: bytes
    """
    with open(path, 'rb') as f:
        data = f.read()
    return data


def build_header(key, value):
    """
    Returns a header built from a key and a value.
    :param key: The key.
    :type key: str
    :param value: The value.
    :type value: Any
    :return: The header encoded.
    :rtype: bytes
    """
    return f'{key}: {value}{END_LINE}'.encode()


def handle_client(client_socket):
    """
    Receives a request, processes it, and sends a response.
    :param client_socket: The socket.
    :type client_socket: socket.socket
    :return: None.
    """
    request, body, body_type = receive_http_request(client_socket)
    is_valid, uri, params = validate_request(request)
    logging.info(f'HTTP request valid: {is_valid}')
    logging.info(f'Requested URI: {uri}')

    if uri == '/calculate-next':
        num = str(int(params['num']) + 1)
        response = f'{HTTP_VERSION} 200 OK\r\nContent-Length: {len(num)}\r\nContent-Type: text/plain\r\n\r\n{num}'.encode()
        send_response(client_socket, response)
        return
    elif uri == '/calculate-area':
        width = int(params['width'])
        height = int(params['height'])
        area = str(width * height / 2)
        response = f'{HTTP_VERSION} 200 OK\r\nContent-Length: {len(area)}\r\nContent-Type: text/plain\r\n\r\n{area}'.encode()
        send_response(client_socket, response)
        return
    elif uri == '/upload':
        with open(f'{UPLOAD_DIR}/{params['file-name']}', 'wb') as f:
            f.write(body)
        response = f'{HTTP_VERSION} 200 OK\r\n\r\n'.encode()
        send_response(client_socket, response)
        return

    status_code = get_status_code(is_valid, uri)
    body = b''

    response = f'{HTTP_VERSION} {status_code} {STATUS_MSG[status_code]}{END_LINE}'.encode()

    if status_code == 302:
        response += build_header('Location', '/')
    elif status_code == 200 or status_code == 404:
        if status_code == 200:
            file_path = get_file_path(uri)
        else:
            file_path = NOT_FOUND_FILE

        body = read_file(file_path)
        name, ext = os.path.splitext(file_path)
        response += build_header('Content-Length', len(body))
        response += build_header('Content-Type', TYPES[ext])

    response += END_LINE.encode()
    response += body

    send_response(client_socket, response)
    logging.info(f'Sending client a response, status code: {status_code}')


def main():
    """
    The main function.
    :return: None.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_LEN)
        logging.debug('Listening for connections...')
        while True:
            client_socket, client_addr = server_socket.accept()
            try:
                logging.info(f'Connected to client at address {client_addr}')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print(f'client socket error: {str(err)}')
                logging.error(f'Error at client socket: {str(err)}')
            finally:
                client_socket.close()
                logging.debug(f'Client at address {client_addr} disconnected.')
    except socket.error as err:
        print(f'server socket error: {str(err)}')
        logging.error(f'Error at server socket: {str(err)}')
    finally:
        server_socket.close()
        logging.debug('Server socket closed.')


if __name__ == '__main__':
    assert validate_request(['GET / HTTP/1.1']) == (True, '/', {})
    assert validate_request(['GET /index.html HTTP/1.1']) == (True, '/index.html', {})
    assert validate_request(['GET /moved HTTP/1.1']) == (True, '/moved', {})
    assert validate_request(['GET HTTP/1.1']) == (False, None, None)
    assert validate_request(['HAHA / HTTP/1.1']) == (False, None, None)
    assert validate_request(['GET / HELLO-THERE/GENERAL-KENOBI']) == (False, None, None)

    if not os.path.isdir(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
