#!/usr/bin/env python
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

import os
import sys
import environ

def main():
    env = environ.Env(
        # set casting, default value
        DEBUG=(bool, False)
    )
    environ.Env.read_env(env_file=os.path.join(os.getcwd(), '.env'))
    RUN_ENV = env.str('RUN_ENV', 'local')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.' + RUN_ENV)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()