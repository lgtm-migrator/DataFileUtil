"""
Fetch the file name from a remote URL.
"""
from requests.cookies import RequestsCookieJar
from typing import Optional
from urllib.parse import urlparse
from uuid import uuid4
import os
import requests

# Local
from DataFileUtil.implementation import log


def retrieve_filename(file_url: str, cookies: Optional[RequestsCookieJar] = None) -> str:
    """
    Fetch the file name from a URL using the Content-Disposition header,
    falling back to the filename found in the URL itself. We shorten any
    filename to at most 255 characters to avoid any filesystem errors.
    If we are unable to retrieve a filename from either the header or URL path,
    then we generate a UUID and use that (without any extension).
    Args:
        file_url: HTTP(S) URL of the file to retrieve
    Returns:
        A file name using data from the given URL
    """
    try:
        # Fetch the headers
        with requests.get(file_url, cookies=cookies, stream=True) as response:
            try:
                content_disposition = response.headers['content-disposition']
            except KeyError:
                log('Parsing file name directly from URL')
                url = urlparse(file_url)
                file_name = os.path.basename(url.path)
            else:
                file_name = content_disposition.split('filename="')[-1].split('";')[0]
    except Exception as error:
        error_msg = 'Cannot connect to URL: {}\n'.format(file_url)
        error_msg += 'Exception: {}'.format(error)
        raise ValueError(error_msg)
    # Shorten any overly long filenames to avoid OSErrors
    # Our practical limit is 255 for eCryptfs
    if len(file_name) > 255:
        (basename, ext) = os.path.splitext(file_name)
        file_name = basename[0:255-len(ext)] + ext
    file_name = file_name.strip()
    if len(file_name) == 0:
        # Handle the case where there is no URL filepath, and no content header
        # We just generate a unique name
        file_name = str(uuid4())
    log(f'Retrieved file name: {file_name}')
    return file_name
