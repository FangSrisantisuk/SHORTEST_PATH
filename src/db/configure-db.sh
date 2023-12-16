#!/bin/bash

# Wait 60 seconds for SQL Server to start up by ensuring that
# calling SQLCMD does not return an error code, which will ensure that sqlcmd is accessible
# and that system and user databases return "0" which means all databases are in an "online" state
# https://docs.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-databases-transact-sql?view=sql-server-2017

DBSTATUS=1
ERRCODE=1
i=0

while [[ $DBSTATUS -ne 0 ]] && [[ $i -lt 60 ]] && [[ $ERRCODE -ne 0 ]]; do
	i=$i+1
	DBSTATUS=$(/opt/mssql-tools/bin/sqlcmd -h -1 -t 1 -U sa -P $MSSQL_SA_PASSWORD -Q "SET NOCOUNT ON; Select SUM(state) from sys.databases")
	ERRCODE=$?
	sleep 1
done

if [ $DBSTATUS -ne 0 ] OR [ $ERRCODE -ne 0 ]; then
	echo "SQL Server took more than 60 seconds to start up or one or more databases are not in an ONLINE state"
	exit 1
fi

# Get Environment variables or use default values
SQL_DEFAULT_DB="${SQL_DEFAULT_DB:-TestDB}"
SQL_DEFAULT_PASSWORD="${SQL_DEFAULT_PASSWORD:-Password@123456}"
SQL_DEFAULT_USER="${SQL_DEFAULT_USER:-db_app_dev}"

# Dynamically set database name, user, password based on environment variables
sed -i -e "s/SQL_DEFAULT_DB/$SQL_DEFAULT_DB/g" -e "s/SQL_DEFAULT_USER/$SQL_DEFAULT_USER/g" -e "s/SQL_DEFAULT_PASSWORD/$SQL_DEFAULT_PASSWORD/g" setup.sql

# Entry point
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD -d master -i setup.sql