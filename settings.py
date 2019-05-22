"""
.. data:: MAJOR_RELEASE_NUMBER

   miniSQL major release version

.. data:: MINOR_RELEASE_NUMBER

   miniSQL minor release version

.. data:: PATCH_RELEASE_NUMBER

   miniSQL patch release version

.. data:: LOGO

   miniSQL ascii logo

.. data:: DB_STORAGE_FILE

   where database records stored

.. data:: DB_ALLOWED_FIELDS

   allowed field names for a database record

.. data:: DB_RECORD_SIZE

   number of bytes per record

.. data:: DB_RECORD_NAME_SIZE

   size of field name in bytes

.. data:: DB_FIELD_DATA_SIZE

   size of field data in bytes

.. data:: DB_ENCODING

   encoding used for strings

.. data:: SHELL_INTRO

   intro message displayed in minisql shell

.. data:: SHELL_PROMPT

   user prompt displayed in minisql shell

.. data:: SHELL_HISTORY_FILE

   stores minisql shell commands for command history lookup

.. data:: SHELL_HISTORY_LENGTH

   number of lines of history to store
"""

MAJOR_RELEASE_NUMBER = 1
MINOR_RELEASE_NUMBER = 0
PATCH_RELEASE_NUMBER = 0

LOGO = ("        _       _  _____  _____  __    \n"
        " _____ |_| ___ |_||   __||     ||  |   \n"
        "|     || ||   || ||__   ||  |  ||  |__ \n"
        "|_|_|_||_||_|_||_||_____||__  _||_____|\n"
        "                            |__|       \n")

DB_STORAGE_FILE = 'db.minisql'
DB_ALLOWED_FIELDS = {'a1', 'a2', 'a3', 'a4'}
DB_RECORD_SIZE = 40
DB_RECORD_NAME_SIZE = 18
DB_FIELD_DATA_SIZE = 4
DB_ENCODING = 'utf-8'


SHELL_INTRO = ("Welcome to the miniSQL shell! Your running Version ({major}.{minor}.{patch}).\n"
               "Commands end with a ';' and support tab autocomplete and history (up/down keys).\n"
               "Type 'h;' or 'help;' to list possible commands.\n".format(
                major=MAJOR_RELEASE_NUMBER, minor=MINOR_RELEASE_NUMBER, patch=PATCH_RELEASE_NUMBER))
SHELL_PROMPT = "miniSQL> "
SHELL_HISTORY_FILE = "minisql_history"
SHELL_HISTORY_LENGTH = 1000
