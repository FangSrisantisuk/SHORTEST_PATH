from typing import Literal

from pydantic import BaseModel
from pydantic import constr, model_validator
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, \
    UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Devices(Base):
    __tablename__ = "devices"
    #
    name: Mapped[str] = mapped_column(String(30), primary_key=True)
    isSource: Mapped[bool] = mapped_column(Boolean, nullable=False)
    isDest: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[int] = mapped_column(Integer, default=1, nullable=True)

    # Defining relationship with Connections table
    src_con: Mapped[list["Connections"]] = relationship(
        back_populates="src_dev",
        foreign_keys="Connections.src",
        cascade="all,delete"
    )

    dst_con: Mapped[list["Connections"]] = relationship(
        back_populates="dst_dev",
        foreign_keys="Connections.dst",
        cascade="all,delete"
    )

    def __repr__(self):
        return (f"(Name: {self.name}, IsSource: {self.isSource}, IsDest: "
                f"{self.isDest}, Status: {self.status}, Cost: {self.cost})")

    __table_args__ = (
        CheckConstraint("~(isSource & isDest) > 0", "nand_src_dest"),
        CheckConstraint("status in (0, 1, 2)", "valid_status"),
    )


class Connections(Base):
    __tablename__ = "connections"
    id: Mapped[int] = mapped_column(primary_key=True)
    src: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("devices.name", ondelete="NO ACTION"),
        nullable=False
    )
    dst: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("devices.name", ondelete="NO ACTION"),
        nullable=False
    )
    cost: Mapped[int] = mapped_column(Integer, default=1, nullable=True)

    # Defining relationships:
    # src and dst are foreign keys referencing name in devices
    src_dev: Mapped["Devices"] = relationship(
        back_populates="src_con",
        foreign_keys="Connections.src"
    )

    dst_dev: Mapped["Devices"] = relationship(
        back_populates="dst_con",
        foreign_keys="Connections.dst"
    )

    component: Mapped["ComponentPaths"] = relationship(
        back_populates="conn",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"(Src: {self.src}, Dest: {self.dst})"

    # Defining Constraints:
    __table_args__ = (
        CheckConstraint(  # No self loop allowed
            "src<>dst",
            "non_self_loop",
        ),
        # Only one permutation of src,dst is allowed
        UniqueConstraint("src", "dst", name="src_dst_unique"),
        UniqueConstraint("dst", "src", name="dst_src_unique")
    )


class BestPaths(Base):
    __tablename__ = "bestpaths"
    id: Mapped[int] = mapped_column(primary_key=True)
    src: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("devices.name", ondelete="NO ACTION"),
    )
    dst: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("devices.name", ondelete="NO ACTION"),
    )

    # Relationship of foreign key
    components: Mapped[list["ComponentPaths"]] = relationship(
        back_populates="path",
        cascade="all, delete",
    )

    # Defining Constraint
    __table_args__ = (
        CheckConstraint(  # No self loop allowed
            "src<>dst",
            "best_path_non_self_loop",
        ),
    )


class ComponentPaths(Base):
    __tablename__ = "componentpaths"

    id: Mapped[int] = mapped_column(primary_key=True)

    pathID: Mapped[int] = mapped_column(ForeignKey("bestpaths.id", ondelete="CASCADE"))
    connID: Mapped[int] = mapped_column(
        ForeignKey("connections.id", ondelete="CASCADE")
        )

    # Relationship of foreign key
    path: Mapped["BestPaths"] = relationship(
        back_populates="components",
        cascade="all,delete"
    )
    conn: Mapped["Connections"] = relationship(
        back_populates="component",
    )


class DeviceData(BaseModel):
    name: constr(to_upper=True, strip_whitespace=True, max_length=30)
    isSource: bool
    isDest: bool
    status: Literal[0, 1, 2] | None = None
    cost: int

    @model_validator(mode="after")
    def check_nan_src_dst(self):
        if not (self.isSource and self.isDest):
            return self
        raise ValueError("Cannot be both source and dest")

    class Config:
        orm_mode = True


class ConnectionData(BaseModel):
    src: constr(to_upper=True, strip_whitespace=True, max_length=30)
    dst: constr(to_upper=True, strip_whitespace=True, max_length=30)
    cost: int

    @model_validator(mode="after")
    def check_src_ne_dst(self):
        if self.src == self.dst:
            raise ValueError(f"Self loop is not allowed. Src and Dst must be different")
        return self

    class Config:
        orm_mode = True
