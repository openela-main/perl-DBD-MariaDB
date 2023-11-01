#!/usr/bin/perl

use strict;
use warnings;

use Test::More tests => 7;

# MySQL setup
my $MYSQL_DIR       = $ENV{'MYSQL_DIR'};
my $MYSQL_UNIX_PORT = $ENV{'MYSQL_UNIX_PORT'};
my $MYSQL_PIDFILE   = $ENV{'MYSQL_PIDFILE'};
my $MYSQL_USER      = $ENV{'MYSQL_USER'};
chomp($MYSQL_USER);

# DBD::MariaDB test setup
my $DBD_MARIADB_TESTDB       = $ENV{'DBD_MARIADB_TESTDB'};
my $DBD_MARIADB_TESTHOST     = $ENV{'DBD_MARIADB_TESTHOST'};
my $DBD_MARIADB_TESTSOCKET   = $ENV{'DBD_MARIADB_TESTSOCKET'};
my $DBD_MARIADB_TESTUSER     = $ENV{'DBD_MARIADB_TESTUSER'};
my $DBD_MARIADB_TESTPASSWORD = $ENV{'DBD_MARIADB_TESTPASSWORD'};

my $MYSQLD = '';
my $mysql_version = readpipe("mysql --version");
if ($mysql_version =~ /MariaDB/) {
    system("mysql_install_db --no-defaults --datadir=$MYSQL_DIR --force --skip-name-resolve --explicit_defaults_for_timestamp >/dev/null 2>&1");
    is($?, 0);
    $MYSQLD = '/usr/libexec/mysqld';
} else {
    $MYSQLD = '/usr/sbin/mysqld';
    system("$MYSQLD --no-defaults --initialize-insecure --datadir=$MYSQL_DIR --explicit_defaults_for_timestamp --user=$MYSQL_USER >/dev/null 2>&1");
    is($?, 0);
}

my $cmd = "$MYSQLD --no-defaults --user=$MYSQL_USER --socket=$MYSQL_UNIX_PORT --datadir=$MYSQL_DIR --pid-file=$MYSQL_PIDFILE --explicit_defaults_for_timestamp --skip-networking >/dev/null 2>&1 &";
system($cmd);
is($?, 0);

my $attempts = 0;
while (system("/usr/bin/mysqladmin --user=root --socket=$MYSQL_UNIX_PORT ping >/dev/null 2>&1") != 0) {
    sleep 3;
    $attempts++;
    if ($attempts > 10) {
        fail("skipping test, mariadb/mysql server could not be contacted after 30 seconds\n");
    }
}
ok(1);

system("mysql --socket=$MYSQL_UNIX_PORT --execute \"CREATE USER '$DBD_MARIADB_TESTUSER\@localhost';\" 2>&1");
is($?, 0);
system("mysql --socket=$MYSQL_UNIX_PORT --execute \"CREATE DATABASE IF NOT EXISTS $DBD_MARIADB_TESTDB CHARACTER SET='utf8mb4';\" 2>&1");
is($?, 0);
system("mysql --socket=$MYSQL_UNIX_PORT --execute \"GRANT ALL PRIVILEGES ON $DBD_MARIADB_TESTDB.* TO '$DBD_MARIADB_TESTUSER\@localhost' IDENTIFIED BY '$DBD_MARIADB_TESTPASSWORD';\" 2>&1");
is($?, 0);
system("/usr/bin/mysqladmin --user=$DBD_MARIADB_TESTUSER --password=$DBD_MARIADB_TESTPASSWORD --socket=$DBD_MARIADB_TESTSOCKET ping >/dev/null 2>&1");
is($?, 0);
