
fkey:
ifeq ($(filter fkey,$(MAKECMDGOALS)),fkey)
	$(eval tablename := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)))
	sqlcmd -S 172.18.0.1,1433 -d TestDB -U SA -P Password@123456 -C -Q "EXEC SP_FKEYS @pktable_name='$(tablename)'" -y 10 -Y 10
else
	@echo "Usage: fkey <databaseName.tableName>"
endif

pkey:
ifeq ($(filter pkey,$(MAKECMDGOALS)),pkey)
	$(eval tablename := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)))
	sqlcmd -S 172.18.0.1,1433 -d TestDB -U SA -P Password@123456 -C -Q "EXEC SP_PKEYS @table_name='$(tablename)'" -y 10 -Y 10
else
	@echo "Usage: pkey <databaseName.tableName>"
endif

up:
	docker compose up

down:
	docker compose down

down_volume:
	docker compose down -v
