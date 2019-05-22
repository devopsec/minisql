#!/usr/bin/env python3

# TODO: implement autocomplete feature
# TODO: fix readline history read / write
# TODO: fix error in query execution (double loop? found during inserts)
# TODO: add error handling

import os, sys, stat, re, readline, weakref, struct, socket
import settings


# constants
WHITE_SPACE_NOT_ENCLOSED = re.compile('\s+(?=(?:[^\"\']*\"[^\"\']*\")*[^\"\']*$)|\s+(?=(?:[^\"\']*\'[^\"\']*\')*[^\"\']*$)',
                                      flags=re.MULTILINE|re.DOTALL)
POSSIBLE_SHELL_COMMANDS = {'help', 'insert', 'retrieve', 'delete', 'update', 'quit'}

# functions
def supportsColor(stream):
    """
    Check if terminal supports ASCII color codes\n
    Modified method from Python cookbook, #475186

    :param stream: file stream to check
    :return: True == supported, False == not supported
    """

    if not hasattr(stream, "isatty") or not stream.isatty():
        # auto color only on TTYs
        return False
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False

def printCmdUsage():
    print("|============== miniSQL Cmd Usage ==============|\n"
          "| minisql.py [-h] | [-v] | [-e <query>]         |\n"
          "|================ Cmd Arguments ================|\n"
          "| (no args)        Start miniSQL shell          |\n"
          "| -h               Show this usage information  |\n"
          "| -v               Show miniSQL version         |\n"
          "| -e <query>       Execute miniSQL query        |\n"
          "| -s <ip>:<port>   Serve queries from network   |\n"
          "|================= Extra Notes =================|\n"
          "| miniSQL will execute commands as provided     |\n"
          "| by stdin if redirected in parent shell        |\n"
          "|===============================================|\n")

def printShellUsage():
    print("|============= miniSQL Shell Usage =============|\n"
          "| Keywords are case insensitive                 |\n"
          "| Optionally shortened versions can be used     |\n"
          "| Each record contain a name and 4 fields       |\n"
          "| Fields are restricted to positive integers    |\n"
          "|========= Show this usage information =========|\n"
          "| miniSQL> H;                                   |\n"
          "| miniSQL> HELP;                                |\n"
          "|=============== Insert a record ===============|\n"
          "| miniSQL> I <record> <a1> <a2> <a3> <a4>;      |\n"
          "| miniSQL> INSERT <record> <a1> <a2> <a3> <a4>; |\n"
          "|=============== Retrieve a record =============|\n"
          "| miniSQL> R <record>;                          |\n"
          "| miniSQL> RETRIEVE <record>;                   |\n"
          "| miniSQL> RETRIEVE *;                          |\n"
          "|=============== Delete a record ===============|\n"
          "| miniSQL> D <record>;                          |\n"
          "| miniSQL> DELETE <record>;                     |\n"
          "| miniSQL> DELETE *;                            |\n"
          "|=============== Update a record ===============|\n"
          "| miniSQL> U <record> <field>=<value>;          |\n"
          "| miniSQL> UPDATE <record> <field>=<value>;     |\n"
          "|================ Quit program =================|\n"
          "| miniSQL> Q;                                   |\n"
          "| miniSQL> QUIT;                                |\n"
          "|===============================================|\n")

def printerr(msg):
    if supportsColor(sys.stdout):
        print("\x1b[1;31m[ERROR]: {}\x1b[0m".format(str(msg).strip()))
    else:
        print("[ERROR]: {}".format(str(msg).strip()))

def printwarn(msg):
    if supportsColor(sys.stdout):
        print("\x1b[1;33m[WARNING]: {}\x1b[0m".format(str(msg).strip()))
    else:
        print("[WARNING]: {}".format(str(msg).strip()))

def printdbg(msg):
    if supportsColor(sys.stdout):
        print("\x1b[1;34m[DEBUG]: {}\x1b[0m".format(str(msg).strip()))
    else:
        print("[DEBUG]: {}".format(str(msg).strip()))


def printTable(headers, data, num_rows=None, fmt='block'):
    """
    Print in table format

    :param headers:  list of strings
    :param data:     list of lists (rows)
    :param num_rows: int
    :param fmt:      str format type
    """

    # settings for different formats
    if fmt == 'block':
        col_delim = "||"
        top_section_start = "//"
        top_section_end = "\\\\"
        top_section_row_delim = "="
        top_section_col_delim = "||"
        middle_section_start = "|]"
        middle_section_end = "[|"
        middle_section_row_delim = "="
        middle_section_col_delim = "[]"
        bottom_section_start = "\\\\"
        bottom_section_end = "//"
        bottom_section_row_delim = "="
        bottom_section_col_delim = "||"
        include_top_section = True
        include_middle_sction = True
        include_bottom_section = True
    elif fmt == 'mysql':
        col_delim = "|"
        top_section_start = "+"
        top_section_end = "+"
        top_section_row_delim = "-"
        top_section_col_delim = "+"
        middle_section_start = "+"
        middle_section_end = "+"
        middle_section_row_delim = "-"
        middle_section_col_delim = "+"
        bottom_section_start = "+"
        bottom_section_end = "+"
        bottom_section_row_delim = "-"
        bottom_section_col_delim = "+"
        include_top_section = True
        include_middle_sction = True
        include_bottom_section = True
    elif fmt == 'md':
        col_delim = "|"
        top_section_start = ""
        top_section_end = ""
        top_section_row_delim = "-"
        top_section_col_delim = "|"
        middle_section_start = "|"
        middle_section_end = "|"
        middle_section_row_delim = "-"
        middle_section_col_delim = "|"
        bottom_section_start = ""
        bottom_section_end = ""
        bottom_section_row_delim = "-"
        bottom_section_col_delim = "|"
        include_top_section = False
        include_middle_sction = True
        include_bottom_section = False
    elif fmt == 'rst':
        col_delim = "|"
        top_section_start = "+"
        top_section_end = "+"
        top_section_row_delim = "-"
        top_section_col_delim = "+"
        middle_section_start = "+"
        middle_section_end = "+"
        middle_section_row_delim = "="
        middle_section_col_delim = "+"
        bottom_section_start = "+"
        bottom_section_end = "+"
        bottom_section_row_delim = "-"
        bottom_section_col_delim = "+"
        include_top_section = True
        include_middle_sction = True
        include_bottom_section = True
    elif fmt == 'unicode':
        col_delim = "║"
        top_section_start = "╔"
        top_section_end = "╗"
        top_section_row_delim = "═"
        top_section_col_delim = "╦"
        middle_section_start = "╠"
        middle_section_end = "╣"
        middle_section_row_delim = "═"
        middle_section_col_delim = "╬"
        bottom_section_start = "╚"
        bottom_section_end = "╝"
        bottom_section_row_delim = "═"
        bottom_section_col_delim = "╩"
        include_top_section = True
        include_middle_sction = True
        include_bottom_section = True
    else:
        col_delim = ""
        top_section_start = ""
        top_section_end = ""
        top_section_row_delim = ""
        top_section_col_delim = ""
        middle_section_start = ""
        middle_section_end = ""
        middle_section_row_delim = ""
        middle_section_col_delim = ""
        bottom_section_start = ""
        bottom_section_end = ""
        bottom_section_row_delim = ""
        bottom_section_col_delim = ""
        include_top_section = False
        include_middle_sction = False
        include_bottom_section = False

    # calculations for formatting
    num_cols = len(headers)
    col_width = max(len(header) for header in headers) + 2
    col_string = ("{col_delim}{:^{col_width}}" * num_cols) + "{col_delim}"

    # top section
    if include_top_section:
        top_section = top_section_start
        for i in range(num_cols):
            top_section += (top_section_row_delim * col_width)
            if i != num_cols - 1:
                top_section += top_section_col_delim
        top_section += top_section_end
        print(top_section)

    # headers section
    print(col_string.format(*headers, col_width=col_width, col_delim=col_delim))

    # middle section
    if include_middle_sction:
        middle_section = middle_section_start
        for i in range(num_cols):
            middle_section += (middle_section_row_delim * col_width)
            if i != num_cols - 1:
                middle_section += middle_section_col_delim
        middle_section += middle_section_end
        print(middle_section)

    # data section
    i = 0
    if num_rows == None:
        num_rows = len(data)
    for i in range(num_rows):
        row = [str(x) for x in data[i]]
        print(col_string.format(*row, col_width=col_width, col_delim=col_delim))

    # bottom section
    if include_bottom_section:
        bottom_section = bottom_section_start
        for i in range(num_cols):
            bottom_section += (bottom_section_row_delim * col_width)
            if i != num_cols - 1:
                bottom_section += bottom_section_col_delim
        bottom_section += bottom_section_end
        print(bottom_section)
    print('')


def validateStdinReadable():
    """
    Check if stdin has been redirected by parent shell\n

    See the following table for supported input types.\n
    Note that as of python v3.3 symlinks are followed by default.

    +------------+-----------+-----------------+
    | Stdin Type | Supported | Program Context |
    +============+===========+=================+
    | directory  | no        |                 |
    +------------+-----------+-----------------+
    | keyboard   | yes       | miniSQL shell   |
    +------------+-----------+-----------------+
    | storage    | no        |                 |
    +------------+-----------+-----------------+
    | file       | yes       | miniSQL cmd     |
    +------------+-----------+-----------------+
    | symlink    | no        |                 |
    +------------+-----------+-----------------+
    | pipe       | yes       | miniSQL cmd     |
    +------------+-----------+-----------------+
    | socket     | no        |                 |
    +------------+-----------+-----------------+

    :return: not readable == -1, 0 == readable in cmd, 1 == readable in shell
    """

    mode = os.stat(sys.stdin.fileno()).st_mode

    # stdin is a pipe
    if stat.S_ISFIFO(mode):
        return 0
    # stdin is a file
    elif stat.S_ISREG(mode):
        return 0
    # stdin is a keyboard
    elif stat.S_ISCHR(mode):
        return 1
    # stdin is a directory
    elif stat.S_IFDIR(mode):
        return -1
    # stdin is a symlink
    elif stat.S_ISLNK(mode):
        return -1
    # stdin is a socket
    elif stat.S_IFSOCK(mode):
        return -1
    # stdin is a storage device
    elif stat.S_IFBLK(mode):
        return -1
    # stdin is an unknown device type
    else:
        return -1

# classes
class MiniDB():
    """
    Access to DB, lower level storage operations, and higher level api (querying)
    """

    db_file = settings.DB_STORAGE_FILE
    record_size = settings.DB_RECORD_SIZE
    name_size = settings.DB_RECORD_NAME_SIZE
    field_size = settings.DB_FIELD_DATA_SIZE
    encoding = settings.DB_ENCODING

    def __init__(self):
        """
        Database initialization / connection
        """

        if not os.path.exists(self.db_file):
            open(self.db_file, 'wb').close()

        self._stream = open(self.db_file, mode='r+b', buffering=self.record_size)
        self._finalizer = weakref.finalize(self, self.close)

    def close(self):
        """
        Close database connection and cleanup
        """

        self._stream.close()

    def recordExists(self, name):
        """
        Check if database record exists

        :param name: record name
        :type name: str
        :return: True | False
        """

        self._stream.seek(0,0)

        while True:
            record = self._stream.read(self.record_size)

            # EOF hit
            if not record:
                return False

            # recall:  l[from:to]  the to is not zero-indexed
            if record[0:self.name_size].decode(self.encoding).rstrip('\0') == name:
                return True

    def getRecord(self, name):
        """
        Get record from database

        :param name: record name
        :type name: str
        :return: tuple(<name>, <a1>, <a2>, <a3>, <a4>) | None
        """

        self._stream.seek(0,0)

        while True:
            record = self._stream.read(self.record_size)

            # EOF hit
            if not record:
                return None

            if record[0:self.name_size].decode(self.encoding).rstrip('\0') == name:
                return (
                    record[0:self.name_size].decode(self.encoding).rstrip('\0'),
                    *struct.unpack('>IxIxIxI', record[19:38])
                )

    def getRecords(self):
        """
        Get aal records from database

        :param name: record name
        :type name: str
        :return: list(tuple(<name>, <a1>, <a2>, <a3>, <a4>)) | [()]
        """

        self._stream.seek(0,0)

        records = []

        while True:
            record = self._stream.read(self.record_size)

            # EOF hit
            if not record:
                return records

            records.append((
                record[0:self.name_size].decode(self.encoding).rstrip('\0'),
                *struct.unpack('>IxIxIxI', record[19:38])
            ))



    def createRecord(self, name, a1, a2, a3, a4):
        """
        Create a record in the database

        :param name: record name
        :type name: str
        :param a1: field data
        :type a1: int
        :param a2: field data
        :type a2: int
        :param a3: field data
        :type a3: int
        :param a4: field data
        :type a4: int
        :return: True | False
        """

        if self.recordExists(name):
            printerr('record already exists')
            return False

        try:
            # number of bytes per character changes per encoding
            # encode record name first and make sure we're within limits
            name_enc = name.encode(self.encoding)
            name_enc = name_enc + b'\x00' * (self.name_size - len(name_enc))
            if len(name_enc) > self.name_size:
                printerr('record name is invalid')
                return False

            # number of bytes per integer varies in python (dynamic)
            # encode as 32bit unsigned integer for static size
            a1_enc = struct.pack('>I', a1)
            a2_enc = struct.pack('>I', a2)
            a3_enc = struct.pack('>I', a3)
            a4_enc = struct.pack('>I', a4)

        except:
            printerr('encoding failed.. invalid data')
            return False

        self._stream.write(name_enc + b'\t' + a1_enc + b'\t' + a2_enc + b'\t' + a3_enc + b'\t' + a4_enc + b'\r\n')
        return True

    def updateRecord(self, name, a1=None, a2=None, a3=None, a4=None):
        """
        Update a record in the database

        :param name: record name
        :type name: str
        :param a1: field data
        :type a1: int
        :param a2: field data
        :type a2: int
        :param a3: field data
        :type a3: int
        :param a4: field data
        :type a4: int
        :return: True | False
        """

        a1_enc, a2_enc, a3_enc, a4_enc = None, None, None, None

        if not self.recordExists(name):
            printerr('record does not exist')
            return False

        self._stream.seek(-self.record_size, 1)

        try:
            # number of bytes per character changes per encoding
            # encode record name first and make sure we're within limits
            name_enc = name.encode(self.encoding)
            name_enc = name_enc + b'\x00' * (self.name_size - len(name_enc))
            if len(name_enc) > self.name_size:
                printerr('record name is invalid')
                return False

            # number of bytes per integer varies in python (dynamic)
            # encode as 32bit unsigned integer for static size
            if a1:
                a1_enc = struct.pack('>I', a1)
            if a2:
                a2_enc = struct.pack('>I', a2)
            if a3:
                a3_enc = struct.pack('>I', a3)
            if a4:
                a4_enc = struct.pack('>I', a4)

        except:
            printerr('encoding failed.. invalid data')
            return False

        # if the transaction isnt rolled back above, go ahead and write
        if a1_enc:
            offset = self.name_size + 1
            self._stream.seek(offset, 1)
            self._stream.write(a1_enc)
            self._stream.seek(-offset - self.field_size, 1)
        if a2_enc:
            offset = self.name_size + 1 + self.field_size + 1
            self._stream.seek(offset, 1)
            self._stream.write(a2_enc)
            self._stream.seek(-offset - self.field_size, 1)
        if a3_enc:
            offset = self.name_size + 1 + (self.field_size + 1) * 2
            self._stream.seek(offset, 1)
            self._stream.write(a3_enc)
            self._stream.seek(-offset - self.field_size, 1)
        if a4_enc:
            offset = self.name_size + 1 + (self.field_size + 1) * 3
            self._stream.seek(offset, 1)
            self._stream.write(a4_enc)
            self._stream.seek(-offset - self.field_size, 1)

        return True

    def deleteRecord(self, name):
        """
        Delete a record from the database

        :param name: record to delete
        :type name: str
        :return: True | False
        """

        if not self.recordExists(name):
            printerr('record does not exist')
            return False

        # end of record
        marker = self._stream.tell() - self.record_size

        # reading into memory and rewriting won't work with very large files
        data = self._stream.read()
        self._stream.seek(marker, 0)
        self._stream.truncate()
        self._stream.write(data)

    def deleteRecords(self):
        """
        Delete all records from the database

        :return: True | False
        """

        self._stream.seek(0,0)
        self._stream.truncate()

    def query(self, query_string):
        """
        Interface to query the database

        :param query_string: queries to run
        :return: True if they succeed, false if they fail
        """

        return self.interpretQueries(self.parseQueries(query_string))

    def parseQueries(self, raw_queries):
        """
        Parse input into interpretable queries based on a SQL-like syntax\n
        Queries are delimited by a semicolon and query commands are delimited by whitespace

        :param raw_queries: command string input
        :return: list of queries to execute
        """

        query_strings = []
        for x in raw_queries.split(';'):
            x = x.strip()
            if len(x) > 0:
                query_strings.append(x)
        return [WHITE_SPACE_NOT_ENCLOSED.split(query) for query in query_strings]


    def interpretQueries(self, queries):
        """
        Interpret queries as a list of commands to execute in miniSQL language

        :param queries: list of queries to process
        :return: False to exit, True to continue (applicable to miniSQL shell)
        """

        for query in queries:
            i = 0

            while i < len(query):
                cmd = query.pop(0)
                i += 1

                if cmd.lower() in {'q', 'quit'}:
                    return False


                elif cmd.lower() in {'h', 'help'}:
                    printShellUsage()
                    return True


                elif cmd.lower() in {'i', 'insert'}:
                    if len(query) == 0:
                        printerr("insert command requires a record")
                        return True

                    record_name = str(query.pop(0))
                    i += 1

                    if len(query) != 4:
                        printerr("insert command requires 4 values")
                        return True

                    # data type conversion and simple checks
                    try:
                        data = []

                        for j in range(4):
                            val = int(query.pop(0))
                            i += 1

                            if val < 0:
                                printerr("insert command value '{}' is invalid".format(val))
                                return True

                            data.append(val)

                    except TypeError:
                        printerr("insert command field type mismatch")
                        return True

                    if self.createRecord(record_name, *data) == True:
                        print('Query successful! Record created..')


                elif cmd.lower() in {'r', 'retrieve'}:
                    if len(query) == 0:
                        printerr("retrieve command requires a record")
                        return True

                    record_name = str(query.pop(0))
                    i += 1

                    headers = ('Record Name', 'a1', 'a2', 'a3', 'a4')

                    if record_name == '*':
                        records = self.getRecords()
                        if len(records) > 0:
                            printTable(headers, records)
                        else:
                            printwarn('Query returned 0 results..')
                    else:
                        record = self.getRecord(record_name)
                        if record is not None:
                            printTable(headers, [record])
                        else:
                            printwarn('Query returned 0 results..')


                elif cmd.lower() in {'d', 'delete'}:
                    if len(query) == 0:
                        printerr("delete command requires a record")
                        return True

                    record_name = str(query.pop(0))
                    i += 1

                    if record_name == '*':
                        if self.deleteRecords() == True:
                            print('Query successful! Records deleted..')
                    else:
                        if self.deleteRecord(record_name) == True:
                            print('Query successful! Record deleted..')


                elif cmd.lower() in {'u', 'update'}:
                    if len(query) == 0:
                        printerr("update command requires a record")
                        return True

                    record_name = str(query.pop(0))
                    i += 1

                    if len(query) == 0:
                        printerr("update command requires a field and value")
                        return True

                    data = {}
                    j = 0
                    while j < len(query):
                        kv_str = query.pop(0)
                        kv_pair = kv_str.split('=')
                        i += 1

                        # make sure we got field and value
                        if len(kv_pair) != 2:
                            printerr("update command field or value missing")
                            return True

                        # data type conversion and simple checks
                        try:
                            key = str(kv_pair[0])
                            val = int(kv_pair[1])

                            if key not in settings.DB_ALLOWED_FIELDS:
                                printerr("update command field '{}' is invalid".format(kv_pair[0]))
                                return True

                            elif val < 0:
                                printerr("update command value '{}' is invalid".format(kv_pair[1]))
                                return True

                        except TypeError:
                            printerr("update command key or value type mismatch")
                            return True

                        data[key] = val
                        j += 1

                    self.updateRecord(record_name, **data)
                    print('Query successful! Record updated..')


                else:
                    printerr('command "{}" is not recognized'.format(cmd))
                    return True

        return True


class MiniShell():
    """
    Simple shell-like interpreter for miniSQL queries
    """

    intro = settings.SHELL_INTRO
    prompt = settings.SHELL_PROMPT
    history_file = settings.SHELL_HISTORY_FILE
    history_len = settings.SHELL_HISTORY_LENGTH

    def __init__(self):
        """
        Setup shell variables and files for session
        """

        if not os.path.exists(self.history_file):
            open(self.history_file, 'w').close()

        self._db = MiniDB()
        self._finalizer = weakref.finalize(self, self.close)

        # import functools
        # global print
        # print = functools.partial(print, flush=True)

        # setup history file
        readline.read_history_file(self.history_file)
        readline.set_history_length(self.history_len)

    def close(self):
        """
        Close database connection and cleanup
        """

        self._db.close()
        readline.write_history_file(self.history_file)

    def complete(self, text, state):
        """
        Find all possible commands to complete text

        :param text:
        :param state:
        :return:
        """

        match_text = text.lstrip().lower()

        options = [cmd for cmd in POSSIBLE_SHELL_COMMANDS if cmd.startswith(match_text)]
        if state < len(options):
            return options[state]
        else:
            return None

    def start(self):
        """
        Start the shell command interpreter\n
        Accept commands until user quits program
        """

        # setup auto complete
        readline.parse_and_bind('set enable-keypad on')
        readline.set_completer(self.complete)
        readline.set_completer_delims('\n;')
        readline.parse_and_bind("tab: complete")

        print(self.intro)

        while True:

            # get input cmds and parse
            raw_queries = input(self.prompt)
            parsed_queries = self._db.parseQueries(raw_queries)

            # DEBUG:
            # print("parsed commands: {}".format(parsed_queries))

            if not self._db.interpretQueries(parsed_queries):
                break

# class MiniServer():
#     """
#     miniSQL DB Server
#     """
#     def __init__(self, host="0.0.0.0", port=8190, buff_size=4096, max_conn=5):
#         """
#         create a server instance
#
#         :param host:
#         :param port:
#         :param buff_size:
#         :param max_conn:
#         """
#
#         self.host = host
#         self.port = port
#         self.buff_size = buff_size
#         self.max_conn = max_conn
#         self.db = MiniDB()
#
#     # def __exit__(self, exc_type, exc_val, exc_tb):
#
#     def recvall(self, conn):
#         """
#         receive all data from client
#
#         :param conn:
#         :return:
#         """
#
#         data = ""
#
#         while True:
#             buff = conn.recv(self.buff_size)
#             if not buff or len(buff) == 0:
#                 break
#             data += buff.decode()
#
#         return data
#
#     def listen(self, callback=print):
#         """
#         listen for connections
#
#         :param callback:
#         :return:
#         """
#
#         serversock = None
#
#         try:
#             serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             serversock.bind((self.host, self.port))
#             serversock.listen(5)
#             printdbg("listening on {host}:{port}".format(host=self.host, port=str(self.port)))
#
#             while True:
#                 senddata = ""
#
#                 conn, srcaddr = serversock.accept()
#                 print('connection established from: {}'.format(srcaddr))
#
#                 print("parsing request data")
#                 recvdata = self.recvall(conn)
#
#                 conn.sendall(senddata.encode())
#
#                 conn.close()
#                 print('connection to: {} closed'.format(srcaddr))
#         finally:
#             serversock.close()


# TODO: exception handling, catch propogated signals here in try, catch block
def main():
    """
    Parse command line arguments and decide how data is processed

    :return: 0 on success, 1 on failure
    """

    args = sys.argv[1:]

    # too many args present
    if len(args) > 2:
        printerr('too many arguments')
        printCmdUsage()
        return 1

    # if no args we need to further process data
    elif len(args) == 0:
        is_readable = validateStdinReadable()

        # stdin can't be read from exit
        if is_readable == -1:
            printerr('stdin is not readable')
            return 1

        # process query if stdin is redirected
        elif is_readable == 0:
            db = MiniDB()
            # TODO: buffer input
            db.query(sys.stdin.read())
            return 0

        # start miniSQL shell if stdin is keyboard
        elif is_readable == 1:
            MiniShell().start()
            return 0

        # something went wrong
        else:
            printerr('unknown error occurred')
            return 1

    # print usage
    elif args[0] == '-h':
        print(settings.LOGO)
        printCmdUsage()
        return 0

    # print version
    elif args[0] == '-v':
        print('miniSQL Version: {major}.{minor}.{patch}'.format(
            major=settings.MAJOR_RELEASE_NUMBER, minor=settings.MINOR_RELEASE_NUMBER, patch=settings.PATCH_RELEASE_NUMBER
        ))
        return 0

    # execute query string
    elif args[0] == '-e':
        args.pop(0)
        if len(args) < 1:
            printerr('missing required arguments')
            return 1

        db = MiniDB()
        db.query(args[0])
        return 0

    # start db server
    elif args[0] == '-s':
        printerr('not yet implemented')
        return 1
        # args.pop(0)
        # if len(args) < 1:
        #     printerr('missing required arguments')
        #     return 1
        #
        # server_info = args[0].split(':')
        # if len(server_info) < 2:
        #     printerr('missing server info')
        #     return 1
        #
        # db = MiniDB()
        # db.query(args[0])
        # return 0

    # incorrect format or wrong args
    else:
        printerr('incorrect format')
        printCmdUsage()
        return 1

if __name__ == '__main__':
    sys.exit(main())
