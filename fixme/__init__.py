
import logging
import subprocess
import urllib
from typing import List, Tuple


def cmd(cmd: List[str]) -> Tuple[int, str]:
    '''
    Executes a command line.

    Example:
    ```python
    cmd_args = ['ls', '-lah']
    exit_code, response = cmd(cmd_args)
    ```
    '''
    cmdline = ' '.join(cmd)
    logging.debug(f'{cmdline}')
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = child.communicate()[0]
    return (child.returncode, output.decode('utf-8'))


def request(method: str, url: str, data=None, headers=None, context=None):
    '''
    Wrapper around `urllib` to match `requests` API.

    To better debug or troubleshoot, the following may be useful:

    ```python
    http.client.HTTPConnection.debuglevel = 1
    https_old_init = urllib.request.HTTPSHandler.__init__

    def https_new_init(self, debuglevel=None, context=None, check_hostname=None):
        debuglevel = debuglevel if debuglevel is not None else http.client.HTTPSConnection.debuglevel
        https_old_init(self, debugleve, context, check_hostname)

    urllib.request.HTTPSHandler.__init__ = https_new_init
    ```

    Keyword arguments
        method -- one of [GET, PUT, POST]
        url -- the URL to transmit to
    '''
    logging.debug(f'{method.upper()} {url}')
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    with urllib.request.urlopen(req, context=context) as resp:
        return resp.read().decode('utf-8')
