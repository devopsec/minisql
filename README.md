# miniSQL

## Simple Binary DB and Querying Language

A simple static indexing storage dbms and querying language

### Requirements

- python ver >= 3.4

Install the python libraries using pip:

```
pip3 install -r requirements.txt
```

### Setup

Settings can be changed in the [settings.py](settings.py) file per your environment.

### Usage

Start the miniSQL cmdline shell:

```
python3 minisql.py
```

Run queries from the terminal:

```
python3 minisql.py -e '<your query>'
```

Pipe queries to miniSQL:

```
echo '<your query>' | python3 minisql.py
```

Input queries from a file:

```
python3 minisql.py < cmds.minisql
```

Start miniSQL DB Server:

```
python3 minisql.py -s <host>:<port>
```

Show the help options:

```
python3 minisql.py -h
```

Show version info:

```
python3 minisql.py -v
```

### Documentation

See the [miniSQL documentation](docs/build/html/index.html) for information on query syntax and database implementation

### Debugging

To debug the raw DB queries you can open up the database file in another stream.
Using the following command in a seperate terminal you can see a more readable output.

```
tail -c +0 -f db.minisql | hexdump -e '18/1 "%_c" 1/1 "%c" 4/1 "%d" 1/1 "%c" 4/1 "%d" 1/1 "%c" 4/1 "%d" 1/1 "%c" 4/1 "%.1d" 2/1 "%_c" "\n"'
```
