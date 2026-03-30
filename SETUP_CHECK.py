import sys
import subprocess
import os

def check_python_version():
    required_version = (3, 6)
    current_version = sys.version_info
    if current_version < required_version:
        print(f"Python version must be at least {required_version[0]}.{required_version[1]}.")
        return False
    else:
        print("Python version is compatible.")
        return True


def check_pip():
    try:
        subprocess.check_call(['pip', '--version'])
        print("Pip is installed.")
    except subprocess.CalledProcessError:
        print("Pip is not installed!")


def check_api_keys():
    api_keys = ['API_KEY_1', 'API_KEY_2']  # Replace these with your actual environment variable names
    for key in api_keys:
        if os.getenv(key) is None:
            print(f"{key} is not set!")
        else:
            print(f"{key} is set.")


def check_virtual_environment():
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Virtual environment is activated.")
    else:
        print("Virtual environment is not activated!")


def main():
    print("Running pre-flight checklist...")
    check_python_version()
    check_pip()
    check_api_keys()
    check_virtual_environment()


if __name__ == '__main__':
    main()