import argparse
import os

import pandas as pd
from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schema import Base, Connections, Devices

# Load environment variables
DATABASE = "mssql"
DIALECT = "pyodbc"
DB_USR = os.getenv("DB_USR", "db_app_dev")
DB_PASSWD = os.getenv("DB_PASSWD", "Password@123456")
DB_PORT = os.getenv("DB_PORT", 1433)
DB_NAME = os.getenv("DB_NAME", "TestDB")


def process_csv(df: pd.DataFrame):
    devices = set()
    connections = set()
    for i in range(len(df)):
        if pd.isna(df.loc[i, "Plant Item"]):
            continue
        name = df.loc[i, "Plant Item"]
        isSource = df.loc[i, "Is Source"]
        isDest = df.loc[i, "Is Destination"]
        src = df.loc[i, "Connect from"]
        dst = df.loc[i, "Connect to"]
        if not (pd.isna(src)):
            connections.add((src, name))
        if not (pd.isna(dst)):
            connections.add((name, dst))
        devices.add((name, isSource, isDest))
    devices = [Devices(name=item[0], isSource=item[1], isDest=item[2]) for item in devices]
    connections = [Connections(src=item[0], dst=item[1]) for item in connections]
    return devices, connections


def bulk_insert(devices, connections, Session):
    with Session() as session:
        session.add_all(devices)
        session.add_all(connections)
        session.commit()


def create_parser():
    parser = argparse.ArgumentParser("Driver for Bulk Insert")
    parser.add_argument("--host", default="172.18.0.1", help="Host IP Address", type=str)
    parser.add_argument("--file", default="InputData.csv", help="Path to csv file to process", type=str)
    return parser.parse_args()


if __name__ == "__main__":
    args = create_parser()

    # Read df
    df = pd.read_csv(args.file)

    # Make session and engine
    connection_url = URL.create(
        f"{DATABASE}+{DIALECT}",
        username=DB_USR,
        password=DB_PASSWD,
        host=args.host,
        port=DB_PORT,
        database=DB_NAME,
        query={
            "driver": "ODBC Driver 17 for SQL Server",
            "TrustServerCertificate": "yes",
        }
    )

    engine = create_engine(connection_url)
    Session = sessionmaker(engine)
    Base.metadata.create_all(engine)
    devices, connections = process_csv(df)

    # Mass insert
    bulk_insert(devices, connections, Session)
