
use warnings;
use DBI;
use File::Spec;
use Test::More;

my $hostname= "saorap71.dtcc.com";
my $user = 'skarothi';             # Change me
my $pass = 'Work4dtcc';             # Change me
my $conn = 'DBI:Oracle:host=saorap71.dtcc.com;sid=TMQWDP'; # Change me

#ORACLE_BASE:C:\app\skarothi\product\11.2.0\client_1
#ORACLE_HOME:C:\app\skarothi\product\11.2.0\client_1

$ORACLE_BASE="C:/APPS/oracle/product/11.2.0";
$ORACLE_HOME="${ORACLE_BASE}/client_1";
$TNS_ADMIN="${ORACLE_HOME}/network/admin";


ok ${ORACLE_BASE}, '$ORACLE_BASE env var is defined';
ok ${ORACLE_HOME}, '$ORACLE_HOME env var is defined';
ok ${TNS_ADMIN},   '$TNS_ADMIN env var is defined';

ok -d ${ORACLE_BASE}, '$ORACLE_BASE dir exists';
ok -d ${ORACLE_HOME}, '$ORACLE_HOME dir exists';
ok -e File::Spec->catfile(${TNS_ADMIN}, 'tnsnames.ora'), 'tnsnames.ora exists';

ok my $dbh = DBI->connect($conn, $user, $pass,{ PrintError => 1, }), 'database connection';
print "Successfully connected \n";
done_testing