import uuid
from copy import deepcopy

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class AcademicModel(Base):
    __tablename__ = "academics"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name = Column(String(100), unique=True)

    groups = relationship("GroupModel", back_populates="academic",
                          primaryjoin='AcademicModel.guid == GroupModel.academic_guid', lazy='joined')

    def __deepcopy__(self, memo):
        result = AcademicModel
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == '_sa_instance_state':
                setattr(result, k, None)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result
