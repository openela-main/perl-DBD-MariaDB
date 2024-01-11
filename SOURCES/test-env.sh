#!/usr/bin/bash

# MariaDB setup
export MYSQL_DIR=$PWD/t/testdb
export MYSQL_UNIX_PORT=$MYSQL_DIR/mysql.sock
export MYSQL_PIDFILE=$MYSQL_DIR/mysql.pid
export MYSQL_USER=`whoami`

# DBD::MariaDB test setup
export DBD_MARIADB_TESTDB=testdb
export DBD_MARIADB_TESTHOST=localhost
export DBD_MARIADB_TESTSOCKET=$MYSQL_UNIX_PORT
export DBD_MARIADB_TESTUSER=testuser
export DBD_MARIADB_TESTPASSWORD=testpassword

