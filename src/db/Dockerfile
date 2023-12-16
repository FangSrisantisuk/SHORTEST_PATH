


FROM mcr.microsoft.com/mssql/server:2022-latest

# Change to root to perform mkdir
USER root
# Create a config directory
RUN mkdir -p /usr/config

# set mssql as owner of the app directory
RUN chown mssql /usr/config

WORKDIR /usr/config

# Bundle config source
COPY src/db/ /usr/config/

RUN echo ls /usr/config
# Grant permissions for to our scripts to be executable
RUN chmod +x /usr/config/entrypoint.sh
RUN chmod +x /usr/config/configure-db.sh

# change back to user mssql
USER mssql

ENTRYPOINT ["./entrypoint.sh"]