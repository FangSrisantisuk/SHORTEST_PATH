## What this repository is for

Build a new image on top of ms-sql image, adding additional configurations with on-start script.

On start script checks for existence of default database, create and add default users. Also grant
all permissions on the default db to default user.

## Environment variables

- ACCEPT_EULA: Accept user agreement?
- MSSQL_SA_PASSWORD: System admin password
- SQL_DEFAULT_DB: default sandbox db
- SQL_DEFAULT_USER: default user with permission on db
- SQL_DEFAULT_PASSWORD: default user's password
