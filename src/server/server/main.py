from typing import Annotated

import fastapi
from fastapi import HTTPException, Query
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.operators import and_

from routing import Graph, k_shortest_path, multilple_dest_path
from schema import Base, ConnectionData, Connections, DeviceData, Devices
from settings import connection_url

# Create engine
engine = create_engine(connection_url, echo=True)
Session = sessionmaker(engine)
Base.metadata.create_all(engine)

# Create fastapi
app = fastapi.FastAPI()

# Type Def
DeviceName = Annotated[str | None, Query(title="Device Name", max_length=30)]
DeviceNameRequired = Annotated[str, Query(title="Device Name", max_length=30)]
ListDeviceNameRequired = Annotated[
    DeviceNameRequired | list[DeviceNameRequired], Query()]


@app.get("/devices/")
def get_devices(
        name: DeviceName = None,
        status: int | None = None
) -> list[DeviceData]:
    with Session() as session:
        query = select(Devices)
        if name is not None:
            query = query.where(Devices.name == name)
        if status is not None:
            query = query.where(Devices.status == status)
        result = session.scalars(query).all()
        if len(result) == 0:
            raise HTTPException(status_code=404, detail="Device not exist on database")
    return result


@app.post("/add/devices/")
def insert_devices(
        devices: DeviceData,
) -> DeviceData:
    with Session() as session:
        src_exist = session.query(Devices).filter(Devices.name == devices.name).first()
        if not src_exist:
            try:
                insert_stmt = insert(Devices).values(devices.model_dump())
                session.execute(insert_stmt)
                session.commit()
            except IntegrityError as e:
                session.rollback()
                raise HTTPException(status_code=406, detail=str(e))
        else:
            raise HTTPException(
                status_code=406,
                detail="A device with the same name already exists. Try updating "
                       "instead!"
            )
    return devices


@app.put("/update/devices/")
def update_devices(
        devices: DeviceData,
) -> DeviceData:
    with Session() as session:
        src_exist = session.query(Devices).filter(Devices.name == devices.name).first()
        if src_exist:
            try:
                update_stmt = update(Devices).where(
                    Devices.name == devices.name
                ).values(devices.model_dump())
                session.execute(update_stmt)
                session.commit()
            except IntegrityError as e:
                session.rollback()
                raise HTTPException(status_code=406, detail=str(e))
        else:
            insert_devices(devices)
    return devices


@app.delete("/delete/devices")
def remove_device(
        name: DeviceName,
):
    with Session() as session:
        try:
            item = session.scalars(
                select(Devices)
                .where(Devices.name == name)
            ).first()
            if item is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cannot delete device that does not exist on db"
                )
            session.delete(item)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(status_code=406, detail=str(e))


@app.get("/connections/")
def get_connections(
        src: DeviceName = None,
        dst: DeviceName = None
) -> list[ConnectionData]:
    with Session() as session:
        query = select(Connections)
        if src is not None:
            query = query.where(Connections.src == src)
        if dst is not None:
            query = query.where(Connections.dst == dst)
        result = session.scalars(query).all()
    return result


@app.post("/add/connections/")
def insert_connections(
        connection: ConnectionData,
) -> dict:
    if connection is None:
        raise HTTPException(status_code=422, detail="Data is None")
    with Session() as session:
        # Validate source and dst existence
        src_exist = session.query(Devices).filter(
            Devices.name == connection.src
        ).first()
        if not src_exist:
            raise HTTPException(
                status_code=406,
                detail=f"Source Device was not registered. Device"
                       f" name: {connection.src}"
            )
        dst_exist = session.query(Devices).filter(
            Devices.name == connection.dst
        ).first()
        if not dst_exist:
            raise HTTPException(
                status_code=406,
                detail=f"Destination Device was not registered. Device"
                       f" name: {connection.dst}"
            )
        # Validate existing anti-path does not exist:
        anti_path_exist = session.query(Connections).filter(
            Connections.src == connection.dst,
            Connections.dst == connection.src
        ).first()
        if anti_path_exist:
            raise HTTPException(
                status_code=406,
                detail=f"Unidirectional requirement violated. An anti"
                       f"-path ({connection.dst},{connection.src}) "
                       f"already exists."
            )

        # Valid existing path:
        path_exist = session.query(Connections).filter(
            Connections.src == connection.src,
            Connections.dst == connection.dst
        ).first()
        if path_exist:
            update_stmt = update(Connections).where(
                and_(
                    Connections.src == connection.src,
                    Connections.dst == connection.dst
                )
            ).values(cost=connection.cost)
            session.execute(update_stmt)
            session.commit()
            return connection.model_dump()
        try:
            # Otherwise execute the insert statement
            insert_stmt = insert(Connections).values(connection.model_dump())
            session.execute(insert_stmt)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(status_code=406, detail=str(e))
    return connection.model_dump()


@app.delete("/delete/connections")
def remove_connections(
        connection: ConnectionData,
):
    with Session() as session:
        try:
            select_stmt = select(Connections).where(
                Connections.src == connection.src,
                Connections.dst == connection.dst
            )
            item = session.scalars(select_stmt).first()
            session.delete(item)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(status_code=406, detail=str(e))


def create_graph_from_database_data() -> Graph:
    # only get available devices
    devices = get_devices(status=0)
    device_list = [(device.name, device.cost) for device in devices]

    # only get connections of available devices
    devices_name = set(device for device, _ in device_list)
    connections = get_connections()
    connection_list = [(con.src, con.dst, con.cost) for con in connections if (con.src in devices_name and con.dst in devices_name)]

    return Graph(device_list, connection_list)


@app.get("/best/paths/")
def get_best_path(
        src: DeviceNameRequired,
        dst: ListDeviceNameRequired,
        num_best_path: int = 5,
):
    if not src:
        raise HTTPException(status_code=404, detail="src device is required")
    if not dst:
        raise HTTPException(status_code=404, detail="dst device is required")
    G = create_graph_from_database_data()

    if not any(src == vertex[0] for vertex in G.vertices):
        raise HTTPException(
            status_code=404, detail=f"src device: {src} not exist on database"
        )
    
    dst_list = dst[0].split(",")
    for i in range(len(dst_list)):
        dst_list[i] = dst_list[i].strip()

    for dst_node in dst_list:
        if not any(dst_node == vertex[0] for vertex in G.vertices):
            raise HTTPException(
                status_code=404, detail=f"dst device {dst_node} not exist on database"
            )

    return k_shortest_path(G, src, dst_list, num_best_path)

@app.get("/combined/paths")
def get_combined_best_path(
    src: DeviceNameRequired,
    dst: ListDeviceNameRequired,
    num_best_path: int=5
):

    if not src:
        raise HTTPException(status_code=404, detail="src device is required")
    if not dst:
        raise HTTPException(status_code=404, detail="dst device is required")
    
    G = create_graph_from_database_data()

    if not any(src == vertex[0] for vertex in G.vertices):
        raise HTTPException(
            status_code=404, detail=f"src device: {src} not exist on database"
        )

    dst_list = dst[0].split(",")

    # only allow entering maximum 2 destinations
    if (len(dst_list) > 2):
        raise HTTPException(
            status_code=404, detail=f"please enter maximum 2 destinations only"
        )
    
    # remove spaces
    for i in range(len(dst_list)):
        dst_list[i] = dst_list[i].strip()

    for dst_node in dst_list:
        if not any(dst_node == vertex[0] for vertex in G.vertices):
            raise HTTPException(
                status_code=404, detail=f"dst device {dst} not exist on database"
            )
        
    result_of_k = k_shortest_path(G, src, dst_list, num_best_path)
    output = multilple_dest_path (G,result_of_k, num_best_path)

    return output