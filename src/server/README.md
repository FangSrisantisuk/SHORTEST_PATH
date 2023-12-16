# DEPRECATED 

# Setting up the database (need to do only once): 

## Download `MySQL`

For reproducibility, I would recommend using an Ubuntu Linux environment, or WSL if you are using windows.

Run the following command: 

```
sudo apt update && sudpo apt upgrade
sudo apt-get install mysql-server
```

## Start `MySQL` server: 

You will need to do this everytime WSL is closed: 

```
sudo /etc/init.d/mysql start
```

This will start `mysql` as a background process, so if it has been killed by accident (either WSL terminal was closed, or 
you actively killed it), just rerun the previous command.

## Create Database and User: 

First run the following commands: 

```
sudo mysql -u root
```

Once you are in `mysql` terminal, create a database 

```
$mysql> CREATE DATABASE SEP;
```

Create a new user: 

```
$mysql> CREATE USER 'yourname'@localhost IDENTIFIED BY 'yourpasswd';
```

Then grant the new user's permission to access the `SEP` database: 

```
$mysql> GRANT ALL PRIVILEGES ON SEP TO `yourname`@localhost;
$mysql> FLUSHS PRIVILEGES;
```

Now exit and check to see if you can enter using the new account: 

```
$mysql> exit;
$bash> mysql -u <yourname>@localhost -p #Need to enter your pwd here
$mysql>show databases; # Should see SEP
$mysql>use SEP; # Enter SEP database 
$mysql>show tables; # Should only see the default table
```

## Save your new access credentials: 

Create a `.env` file in `src/`: 
```
touch src/.env
```

Use a text editor to paste the following information to your `.env` file: 

```
DB_USR="<yourname>"
DB_PASSWD="<yourpassword>"
DB_ADDR="localhost"
DB_NAME="SEP"
```

Remember to replace the field denoted by `<>` with the credentials you just created. 

# Running the program: 

## Run `mysql` server: 

See previous section if you haven't done so.

## Set up `.env` file: 

See previous section if you haven't done so.

## Install poetry and python: version 3.10+:

You can do this in windows: 

```
python -m pip install poetry  
```

Install all required dependencies: 

```
poetry install 
```

## Running the API server: 

```
python -m src.main
```

## Adding demo devices and connections:

### Adding devices
```
curl -X 'POST' \
  'http://127.0.0.1:8000/add/devices/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
{
  "name": "A"
},
{
  "name": "B"
},
{
  "name": "C"
},
{
  "name": "D"
}
]'
```

### Adding connections:

```
curl -X 'POST' \
  'http://127.0.0.1:8000/add/connections/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
{
  "src": "A",
  "dst": "B",
  "cost": 24
},
{
  "src": "A",
  "dst": "C",
  "cost": 3
},
{
  "src": "A",
  "dst": "D",
  "cost": 20
},
{
  "src": "C",
  "dst": "D",
  "cost": 12
}
]'
```

### See available devices: 

```
http://127.0.0.1:8000/devices
```

### See available connections:

```
http://127.0.0.1:8000/connections
```

### See best path from src:

```
http://127.0.0.1:8000/path?src=A
```
Change A to any other source path

## Testing

To run all tests: 

```
poetry run pytest 
```

Or if the previous doesn't work: 

```
poetry shell 
python -m pytest 
```