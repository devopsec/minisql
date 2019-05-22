#!/usr/bin/env python3

# TODO: handle commands from terminal (i.e. using assn3.py -e '')
# TODO: handle commands from stdin
# TODO: allow stdout redirection
# TODO: file handling / hashing records

import os, sys, stat, re, cmd
import settings

# compile once for optimization
WHITE_SPACE_NOT_ENCLOSED = re.compile('\s+(?=(?:[^\"\']*\"[^\"\']*\")*[^\"\']*$)|\s+(?=(?:[^\"\']*\'[^\"\']*\')*[^\"\']*$)',
                                      flags=re.MULTILINE|re.DOTALL)

# modified method from Python cookbook, #475186
def supportsColor(stream):
    """
    Check if terminal supports ASCII color codes

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
    print("|============ miniSQL Cmd Usage ============|"
          "| minisql.py [-h] | [-v] | [-e <query>]     |"
          "|============== Cmd Arguments ==============|"
          "| (no args):   Start miniSQL shell          |"
          "| -h:          Show this usage information  |"
          "| -v:          Show miniSQL version         |"
          "| -e <query>:  Execute miniSQL query        |"
          "|=============== Extra Notes ===============|"
          "| miniSQL will execute commands as provided |"
          "| by stdin if redirected in parent shell    |"
          "|===========================================|")

def printShellUsage():
    print("|=========== miniSQL Shell Usage ===========|"
          "| Keywords are case insensitive             |"
          "| Optionally shortened versions can be used |"
          "|======= Show this usage information =======|"
          "| miniSQL> H;                               |"
          "| miniSQL> HELP;                            |"
          "|============= Insert a record =============|"
          "| miniSQL> I <record>;                      |"
          "| miniSQL> INSERT <record>;                 |"
          "|============= Retrieve a record ===========|"
          "| miniSQL> R <record>;                      |"
          "| miniSQL> RETRIEVE <record>;               |"
          "|============= Delete a record =============|"
          "| miniSQL> D <record>;                      |"
          "| miniSQL> DELETE <record>;                 |"
          "|============= Update a record =============|"
          "| miniSQL> U <record> <field> <value>;      |"
          "| miniSQL> UPDATE <record> <field> <value>; |"
          "|============== Quit program ===============|"
          "| miniSQL> Q;                               |"
          "| miniSQL> QUIT;                            |"
          "|===========================================|")

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
        return True
    # stdin is a file
    elif stat.S_ISREG(mode):
        return True
    # stdin is a keyboard
    elif stat.S_ISCHR(mode):
        return False
    # stdin is a directory
    elif stat.S_IFDIR(mode):
        return False
    # stdin is a symlink
    elif stat.S_ISLNK(mode):
        return False
    # stdin is a socket
    elif stat.S_IFSOCK(mode):
        return False
    # stdin is a storage device
    elif stat.S_IFBLK(mode):
        return False
    # stdin is an unknown device type
    else:
        return False



def parseQueries(raw_queries):
    """
    Parse input into interpretable queries based on a SQL-like syntax\n
    Queries are delimited by a semicolon and query commands are delimited by whitespace

    :param raw_queries: command string input
    :return: list of queries (each as a list of commands)
    """

    query_strings = raw_queries.split(';')
    return [query for query in WHITE_SPACE_NOT_ENCLOSED.split(query_strings)]

def interpretQueries(queries):
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
                if not len(query) > 0:
                    printerr("insert command requires a record")
                    return True

                record = query.pop(0)
                i += 1
                print("insert record {}".format(record))

            elif cmd.lower() in {'r', 'replace'}:
                if not len(query) > 0:
                    printerr("retrieve command requires a record")
                    return True

                record = query.pop(0)
                i += 1
                print("retrieve record {}".format(record))

            elif cmd.lower() in {'d', 'delete'}:
                if not len(query) > 0:
                    printerr("delete command requires a record")
                    return True

                record = query.pop(0)
                i += 1
                print("delete record {}".format(record))

            elif cmd.lower() in {'u', 'update'}:
                if not len(query) > 0:
                    printerr("update command requires a record")
                    return True

                record = query.pop(0)
                i += 1

                if not len(query) > 1:
                    printerr("update command requires a field and value")
                    return True

                field = query.pop(0)
                value = query.pop(0)
                print("update record {} set field {} = {}".format(record, field, value))

            else:
                printerr('command "{}" is not recognized'.format(cmd))
                return True

    return True

class MinisqlShell(cmd.Cmd):
    intro = ("Welcome to the miniSQL shell! Your running Version ({major}.{minor}.{patch}).\n"
             "Commands end with a ';' and support tab autocomplete and history (up/down keys).\n"
             "Type 'h;' or 'help;' to list possible commands.\n".format(
        major=settings.MAJOR_RELEASE_NUMBER, minor=settings.MINOR_RELEASE_NUMBER, patch=settings.PATCH_RELEASE_NUMBER
    ))
    prompt = "miniSQL> "
    file = None

    # ----- basic turtle commands -----
    def do_forward(self, arg):
        'Move the turtle forward by the specified distance:  FORWARD 10'
        forward(*parse(arg))
    def do_right(self, arg):
        'Turn turtle right by given number of degrees:  RIGHT 20'
        right(*parse(arg))
    def do_left(self, arg):
        'Turn turtle left by given number of degrees:  LEFT 90'
        left(*parse(arg))
    def do_goto(self, arg):
        'Move turtle to an absolute position with changing orientation.  GOTO 100 200'
        goto(*parse(arg))
    def do_home(self, arg):
        'Return turtle to the home position:  HOME'
        home()
    def do_circle(self, arg):
        'Draw circle with given radius an options extent and steps:  CIRCLE 50'
        circle(*parse(arg))
    def do_position(self, arg):
        'Print the current turtle position:  POSITION'
        print('Current position is %d %d\n' % position())
    def do_heading(self, arg):
        'Print the current turtle heading in degrees:  HEADING'
        print('Current heading is %d\n' % (heading(),))
    def do_color(self, arg):
        'Set the color:  COLOR BLUE'
        color(arg.lower())
    def do_undo(self, arg):
        'Undo (repeatedly) the last turtle action(s):  UNDO'
    def do_reset(self, arg):
        'Clear the screen and return turtle to center:  RESET'
        reset()
    def do_bye(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        print('Thank you for using Turtle')
        self.close()
        bye()
        return True

    # ----- record and playback -----
    def do_record(self, arg):
        'Save future commands to filename:  RECORD rose.cmd'
        self.file = open(arg, 'w')
    def do_playback(self, arg):
        'Playback commands from a file:  PLAYBACK rose.cmd'
        self.close()
        with open(arg) as f:
            self.cmdqueue.extend(f.read().splitlines())
    def precmd(self, line):
        line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line
    def close(self):
        if self.file:
            self.file.close()
            self.file = None

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))






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

    # print usage
    if args[0] == '-h':
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

        parsed_queries = parseQueries(raw_queries)
        interpretQueries(parsed_queries)
        return 0
    # start miniSQL shell
    else:
        # process query if stdin is redirected

        MinisqlShell().cmdloop()

        # # start the db cmdline (shell-like interface)
        # # accept commands until user quits program
        # while True:
        #     raw_queries = input("db> ")
        #     parsed_queries = parseQueries(raw_queries)
        #     # DEBUG:
        #     # print("parsed commands: {}".format(parsed_cmds))
        #     if not interpretQueries(parsed_queries):
        #         break

    return 0

if __name__ == '__main__':
    sys.exit(main())
