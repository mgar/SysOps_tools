#!/usr/bin/php
<?php
system("ssh root@SECONDARY_MASTER '/etc/init.d/mysql stop'");
system("ssh root@SECONDARY_MASTER 'rm -rfv /var/lib/mysql/*'");
system("innobackupex --stream=tar --host=127.0.0.1 --user=root --password=PASSWORD --slave-info /var/lib/mysql |ssh root@SECONDARY_MASTER \"cd /var/lib/mysql;tar --ignore-zero -xvf -\"");
system("ssh root@SECONDARY_MASTER 'cd /var/lib/mysql;innobackupex --apply-log ./;chown -R mysql:mysql /var/lib/mysql;/etc/init.d/mysql start'");
die;
$binlog = system("ssh root@SECONDARY_MASTER 'cat /var/lib/mysql/xtrabackup_binlog_info'");
$binarr = explode("	",$binlog);
echo "File: $binarr[0]\nPos: $binarr[1]\n";
system("echo \"CHANGE MASTER TO MASTER_HOST='PRIMARY_MASTER', MASTER_USER='replication', MASTER_PASSWORD='replication', MASTER_PORT=3306, MASTER_LOG_FILE='$binarr[0]', MASTER_LOG_POS=$binarr[1], MASTER_CONNECT_RETRY=10\"|mysql -u root -pPASSWORD -hSECONDARY_MASTER");
system("echo \"start slave\"|mysql -u root -pPASSWORD -hSECONDARY_MASTER");

die;

echo "Stopping Slave on Primary Master\n";
system("echo \"stop slave\"|mysql -u root -pPASSWORD -hPRIMARY_MASTER");
sleep(2);
echo "Resetting slave information on Primary Master\n";
system("echo \"reset slave\"|mysql -u root -pPASSWORD -hPRIMARY_MASTER");
sleep(2);
echo "Setting new replication point on primary master\n";
system("echo \"CHANGE MASTER TO MASTER_HOST='SECONDARY_MASTER', MASTER_USER='replication', MASTER_PASSWORD='replication', MASTER_PORT=3306, MASTER_LOG_FILE='wh-prod-mysql-a.000001', MASTER_LOG_POS=1, MASTER_CONNECT_RETRY=10\"|mysql -u root -pPASSWORD -hPRIMARY_MASTER");
echo "Starting slave server\n";
system("echo \"start slave\"|mysql -u root -pPASSWORD -hPRIMARY_MASTER");
