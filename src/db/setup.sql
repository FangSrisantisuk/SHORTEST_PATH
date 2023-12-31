-- Create SQL_DEFAULT_DB if it does not exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SQL_DEFAULT_DB')
BEGIN
  CREATE DATABASE SQL_DEFAULT_DB;
END;
GO
-- Create a Default User and assign to the database if does not exist
USE SQL_DEFAULT_DB
IF NOT EXISTS
    (SELECT name
     FROM sys.database_principals
     WHERE name = 'SQL_DEFAULT_USER')
BEGIN
    CREATE LOGIN SQL_DEFAULT_USER WITH PASSWORD='SQL_DEFAULT_PASSWORD'
    CREATE USER SQL_DEFAULT_USER FOR LOGIN SQL_DEFAULT_USER
    ALTER ROLE db_datareader ADD MEMBER SQL_DEFAULT_USER
    ALTER ROLE db_datawriter ADD MEMBER SQL_DEFAULT_USER
    ALTER ROLE db_backupoperator ADD MEMBER SQL_DEFAULT_USER
    ALTER ROLE db_ddladmin ADD MEMBER SQL_DEFAULT_USER
END