"""
Author: Yoad Winter
Date: 25.1.2024
Description: The server functions for the HTTP server. The parameter body in these functions is used for symmetry.
"""
import os
from globals import *


def func_calculate_next(params, body):
    """
    Returns the next integer after num.
    :param params: Query parameters.
    :type params: dict[str, str]
    :param body: HTTP request body.
    :type body: bytes
    :return: status code, response body, response body type.
    :rtype: tuple[int, bytes, str]
    """
    num = params['num']
    status_code = 400
    res_body = None
    res_body_type = None
    if num.isdigit():
        status_code = 200
        res_body = str(int(num) + 1).encode()
        res_body_type = 'text/plain'
    return status_code, res_body, res_body_type


def func_calculate_area(params, body):
    """
    Returns the area from width and height.
    :param params: Query parameters.
    :type params: dict[str, str]
    :param body: HTTP request body.
    :type body: bytes
    :return: status code, response body, response body type.
    :rtype: tuple[int, bytes, str]
    """
    status_code = 400
    res_body = None
    res_body_type = None
    width, height = params['width'], params['height']
    if width.isdigit() and height.isdigit():
        status_code = 200
        res_body = str(int(width) * int(height) / 2).encode()
        res_body_type = 'text/plain'
    return status_code, res_body, res_body_type


def func_upload(params, body):
    """
    Uploads an image to the folder 'upload'.
    :param params: Query parameters.
    :type params: dict[str, str]
    :param body: HTTP request body.
    :type body: bytes
    :return: status code, response body, response body type.
    :rtype: tuple[int, bytes, str]
    """
    file_name = UPLOAD_DIR + '/' + params['file-name']
    with open(file_name, 'wb') as f:
        f.write(body)
    return 200, None, None


def func_image(params, body):
    """
    Returns an image in the 'public' dir from a name.
    :param params: Query parameters.
    :type params: dict[str, str]
    :param body: HTTP request body.
    :type body: bytes
    :return: status code, response body, response body type.
    :rtype: tuple[int, bytes, str]
    """
    file_name = UPLOAD_DIR + '/' + params['image-name']
    res_body, res_body_type = None, None
    if os.path.isfile(file_name):
        status_code = 200
    else:
        status_code = 404

    if status_code == 200:
        res_body = read_file(file_name)
        name, ext = os.path.splitext(file_name)
        res_body_type = TYPES[ext]
    return status_code, res_body, res_body_type
