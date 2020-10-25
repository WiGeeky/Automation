""" Extract a list of all packages installed from shell history

This module goes through the files of shell history and extracts all packages installed from install commands
Currently, this module supports both bash and zsh history, make an issue for expansion.

Note: Use of bash operators (&, |, ;) is currently unsupported, commands with such characters are skipped
"""
import os 
import re

home = os.getenv("HOME")

PREFIX_LIST = {
    'apt': ['/usr/bin/apt', 'apt install'],
    'snap': ['/usr/bin/snap', 'snap install'],
    'yum': ['/usr/bin/yum', 'yum install']
}


ZSH_CLEANUP = re.compile(r': \d+:\d+;')

class Processor:
    """ Handles file operation and filtering """
    unsupported_operators = ['&', '|', ';', './']
    def __init__(self, prefixes):
        self.prefixes = prefixes
        self.packages = set()

    def _openFile(self, file_path):
        try:
            self.active = True
            self.file = open(file_path, 'r+', errors='ignore')
        except FileNotFoundError:
            self.active = False
            self.file = []
    
    def invoke(self, file_path, processor_function, cleanup_function=None):
        self._openFile(file_path)
        if not self.active:
            return 
        for line in self.file:
            # Find the prefix used
            prefix = None
            for values in prefixes.values():
                if values[1] in line:
                    prefix = values[1]
                    break
            if prefix is None:
                continue

            if cleanup_function is not None:
                line = cleanup_function(line)
            if any(operator in line for operator in self.unsupported_operators):
                continue

            line = line.replace('\n', '')
            self.packages.update(processor_function(line, prefix))
        
        self.packages.remove('') if '' in self.packages else None
        self.file.close()



def simpleProcessor(line, prefix):
    """ Processes a simple history (e.g .bash_history)

    a simple history is defined as a type of history file that contains nothing but one command in each line
    """
    return line.replace(prefix, '').split(' ')


def zshCleanup(line):
    return ZSH_CLEANUP.sub('', line)


def getAvailablePrefixes():
    prefixes = {}
    for key, values in PREFIX_LIST.items():
        if not os.path.exists(values[0]):
            continue
        if os.getenv('USER') != 'root':
            values[1] = 'sudo ' + values[1]
        prefixes[key] = values
    return prefixes


SHELL_LIST = {
    'bash': ['/bin/bash', os.path.join(home, '.bash_history'), simpleProcessor],
    'zsh':  ['/bin/zsh', os.path.join(home, '.zsh_history'), simpleProcessor, zshCleanup],
}

if __name__ == "__main__":
    prefixes = getAvailablePrefixes()
    p = Processor(prefixes)

    for key, values in SHELL_LIST.items():
        if os.path.exists(values[0]):
            p.invoke(*values[1:])
        else:
            print('{} not found, skipping...'.format(key))
    
    print(' '.join(p.packages))