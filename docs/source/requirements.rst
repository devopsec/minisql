====================
Project Requirements
====================

This project was written as an exercise for my Database Systems class.
Here were the requirements for the project.

Summary
=======

For this assignment you will write a fully self-describing program to
perform file operations using dynamic hashing.

The records
===========

Each record will consist of a name field, an eighteen-character string,
which is the key field and four non-negative integers; having field
names a1, a2, a3, and a4.

The file
========

You will use block I/O to perform all operations on the file. A block
size of 40 will be used. Within a block, you should read and write
whole records. The file must be created before use, but not removed
after uses. It should expand and contract as needed.

The Input
=========

Input to your program will consist of commands, one per line, requesting
operations to be performed on the file. Input will come from standard
input. Legal commands are:

***I record*** – Insert record into the file, unless one having the same
key is already there.

***R name*** – Retrieve the record having key name, if it is there.

***D name*** – Delete the record having key name from the file, if it
exists.

***U name a-field name new-value***. Update the given record by finding
it (if it exists) and replacing the given information.

In order to make the input easy to parse:

1. The first character will begin in column one;

2. The elements of each type of input will be separated by single tab
       characters;

3. The name field will contain no tabs;

4. A new line will immediately follow the last element of each command.

5. All input is guaranteed to be correct, so no data validation need be
       performed.

The Output
==========

This program will be fully self-describing, which means that a person
can read only the output file and duplicate by hand the exact actions of
the program on a given input sequence. Hand duplication should be
possible even without availability of the input file.

Deliverables
============

1. A Database using MySQL and an corresponding ER Diagram describing the database.

2. A new DBMS system to fully realize your database.

3. An interface to your DBMS system in PHP.

4. Complete, professionally written documentation.

5. Test input files and commands.

Notes
=====

1. Be sure to include identification information in all of your files and outputs.

2. The program will be tested by redirected standard I/O to and from
files. Be sure that your input echo still works when I/O is redirected.

3. In general, your code should use low-level file I/O. If you are
programming in C, you should use fread, fwrite and fseek for file
I/O. If you are using Java, you probably want to use Buffered Streams.

4. Include test output as well.
