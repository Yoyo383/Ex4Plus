"""
Author: Yoad Winter
Date: 25.1.2024
Description: A very basic HTTP server.
"""
import os
import socket
import logging
import server_funcs
from globals import *


LOG_FORMAT = '[%(levelname)s | %(asctime)s | %(processName)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'


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
    Takes a request and returns its headers as a dict.
    :param lines: The request as lines.
    :type lines: list[str]
    :return: The headers.
    :rtype: dict[str, str]
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
    :return: The HTTP request as a list of its lines, the body, and the body type.
    :rtype: tuple[list[str], bytes, str]
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


def build_response(status_code, body=None, body_type=None, location=None):
    """
    Takes a status code, body, body type and location and builds an HTTP response.
    :param status_code: The status code.
    :type status_code: int
    :param body: The body of the response.
    :type body: bytes | None
    :param body_type: The type of the body.
    :type body_type: str | None
    :param location: The target location (if needed).
    :type location: str | None
    :return: The HTTP response.
    :rtype: bytes
    """
    response = f'{HTTP_VERSION} {status_code} {STATUS_MSG[status_code]}{END_LINE}'.encode()
    if location:
        response += build_header('Location', location)
    if body:
        response += build_header('Content-Length', len(body))
        response += build_header('Content-Type', body_type)
    response += END_LINE.encode()
    if body:
        response += body
    return response


def handle_client(client_socket):
    """
    Receives a request, processes it, and sends a response.
    :param client_socket: The socket.
    :type client_socket: socket.socket
    :return: None.
    """
    response = b''
    status_code = 0
    try:
        request, body, body_type = receive_http_request(client_socket)
        is_valid, uri, params = validate_request(request)
        logging.info(f'HTTP request valid: {is_valid}')
        logging.info(f'Requested URI: {uri}')
        logging.info(f'Query parameters: {params}')

        if uri in SPECIAL_FUNCS_URIS.keys():
            if set(params.keys()) == set(SPECIAL_FUNCS_URIS[uri]):
                # yay getattr() my favorite function
                special_func = getattr(server_funcs, f'func_{uri[1:].replace('-', '_')}')
                # special_func() returns a status code, a body, and a body type no matter what function it is
                status_code, res_body, res_body_type = special_func(params, body)
                response = build_response(status_code, res_body, res_body_type)
            else:
                response = build_response(400)
        else:
            status_code = get_status_code(is_valid, uri)
            res_body = b''
            location = None
            res_body_type = None

            if status_code == 302:
                location = '/'
            elif status_code == 200 or status_code == 404:
                if status_code == 200:
                    file_path = get_file_path(uri)
                else:
                    file_path = NOT_FOUND_FILE

                res_body = read_file(file_path)
                name, ext = os.path.splitext(file_path)
                res_body_type = TYPES[ext]

            response = build_response(status_code, res_body, res_body_type, location)

    except socket.error as err:
        status_code = 500
        response = build_response(status_code)
        print(f'client socket error: {str(err)}')
        logging.error(f'Error at client socket: {str(err)}')

    finally:
        send_response(client_socket, response)
        logging.info(f'Sending client a response, status code: {status_code}')
        client_socket.close()


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
            logging.info(f'Connected to client at address {client_addr}')
            client_socket.settimeout(SOCKET_TIMEOUT)
            # try/except is in handle_client()
            handle_client(client_socket)
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
    assert (validate_request(['POST /haha?hello=there&general=kenobi HTTP/1.1'])
            == (True, '/haha', {'hello': 'there', 'general': 'kenobi'}))
    assert build_response(400) == b'HTTP/1.1 400 BAD REQUEST\r\n\r\n'
    assert (build_response(200, b'8', 'text/plain')
            == b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\nContent-Type: text/plain\r\n\r\n8')
    assert build_response(302, location='/') == b'HTTP/1.1 302 MOVED TEMPORARILY\r\nLocation: /\r\n\r\n'

    if not os.path.isdir(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
