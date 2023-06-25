
import logging
import subprocess
from typing import List, Tuple


def exec_commandline(cmd: List[str]) -> Tuple[int, str]:
    '''
    Executes a command line.

    Example:
    ```python
    cmd_args = ['ls', '-lah']
    exit_code, response = exec_commandline(cmd_args)
    ```
    '''
    cmdline = ' '.join(cmd)
    logging.debug(f'{cmdline}')
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = child.communicate()[0]
    return (child.returncode, output.decode('utf-8'))
