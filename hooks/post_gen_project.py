"""Post gen hook to ensure that the generated project
has only one package management, either pipenv or pip."""
import logging
import os
import shutil
import sys

_logger = logging.getLogger()


def clean_extra_package_management_files():
    """Removes either requirements files and folder or the Pipfile."""
    to_delete = []

    try:
        for file_or_dir in to_delete:
            if os.path.isfile(file_or_dir):
                os.remove(file_or_dir)
            else:
                shutil.rmtree(file_or_dir)
        shutil.copy(".env.example", ".env")
        open("dev.db", 'a').close()
    except OSError as e:
        _logger.warning("While attempting to remove file(s) an error occurred")
        _logger.warning(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    clean_extra_package_management_files()
