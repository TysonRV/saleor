#!/usr/bin/env python3
import os
import sys

import yaml

if __name__ == "__main__":
    os.environ.setdefault("ENV", "DEV")

    if os.path.isfile('env.yml'):
        env_vars = yaml.load(open('env.yml').read())

        for key, value in env_vars[os.getenv('ENV')].items():
            os.environ.setdefault(key, value)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
