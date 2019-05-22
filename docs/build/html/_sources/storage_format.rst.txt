=====================
Storage Specification
=====================

Records are stored in a database file, encoded as binary data.

record storage format:
::

   <record_name>\t<a1>\t<a2>\t<a3>\t<a4>\r\n

miniSQL data constraints:

+------------------+----------------------+----------+
|   storage type   |     data type        |   size   |
+==================+======================+==========+
|    field name    |  string              |   18 B   |
+------------------+----------------------+----------+
|    field data    |  unsigned integer    |  4 B * 4 |
+------------------+----------------------+----------+
|     tab char     |  char                |  1 B * 4 |
+------------------+----------------------+----------+
|   CRLF string    |  char                |   2 B    |
+------------------+----------------------+----------+
|    total record size                    |   40 B   |
+-----------------------------------------+----------+
