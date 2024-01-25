"""
Author: Yoad Winter
Date: 25.1.2024
Description: Global constants and functions for the server.
"""
QUEUE_LEN = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2

END_LINE = '\r\n'
HEADER_KEY_VALUE_SEP = ': '
PARAMETER_SEP = '&'
PARAM_KEY_VALUE_SEP = '='
PARAMETER_BEGIN = '?'

VALID_VERBS = ['GET', 'POST']
HTTP_VERSION = 'HTTP/1.1'
WEB_ROOT = 'webroot'
NOT_FOUND_FILE = 'not-found.html'
UPLOAD_DIR = 'upload'

SPECIAL_URIS = {'/moved': 302, '/forbidden': 403, '/error': 500}
SPECIAL_FUNCS_URIS = {
    '/calculate-next': ['num'],
    '/calculate-area': ['width', 'height'],
    '/upload': ['file-name'],
    '/image': ['image-name']
}
DEFAULT_PATH = '/index.html'
STATUS_MSG = {
    200: 'OK',
    302: 'MOVED TEMPORARILY',
    400: 'BAD REQUEST',
    404: 'NOT FOUND',
    500: 'INTERNAL SERVER ERROR',
    403: 'FORBIDDEN'
}
TYPES = {
    '.html': 'text/html;charset=utf-8',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.css': 'text/css',
    '.js': 'text/javascript;charset=utf-8',
    '.txt': 'text/plain',
    '.ico': 'image/x-icon',
    '.gif': 'image/jpeg',
    '.png': 'image/png'
}


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
