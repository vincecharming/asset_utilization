#
# Vince Charming (c) 2019
#

"""
General utilities used by Test & Road Operations
"""

from uuid import UUID

__author__ = 'vcharming'


def is_valid_uuid(input_uuid):
    """
    Check if the given a UUID is valid or not.
    :param guid: A UUID in question
    :return: True, if valid, else False
    """
    result = True
    # Converts to string
    # Works with or without "-"
    if isinstance(input_uuid, UUID):
        input_uuid = str(input_uuid)
    # Tries to convert a string to a UUID
    try:
        UUID(input_uuid)
    except Exception:
        result = False
    return result
