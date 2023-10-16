from .database import Base
from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import collections


class Group(Base):
    __tablename__ = "groups"

    name = Column(String(10), primary_key=True)
    course = Column(Integer)
    academic_name = Column(String(50))

    lessons = relationship("Lesson", back_populates="group")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    fullname = Column(String(100))
    # url = Column(String(200), unique=True)
    online_url = Column(String(200), nullable=True)
    alt_online_url = Column(String(200), nullable=True)

    lesson_teacher = relationship("LessonTeacher", back_populates="teacher")

    @hybrid_method
    def __repr__(self):
        return f"ModelTeacher:\n   - name: {self.name}\n   - fullname: {self.fullname}\n   - online_url: {self.online_url}\n   - alt_online_url: {self.alt_online_url})"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    time_start = Column(String(50))
    time_end = Column(String(50))
    dot = Column(Boolean, default=False)
    cabinet = Column(String(50))
    type = Column(String(10))
    weeks = Column(String(10))
    name = Column(String(200))
    subgroup = Column(String(100))
    date_start = Column(String(15))
    date_end = Column(String(15))
    day = Column(String(15))

    group_name = Column(String(50), ForeignKey("groups.name"), nullable=False)
    group = relationship("Group", back_populates="lessons")

    lesson_teacher = relationship("LessonTeacher", back_populates="lesson")

    @hybrid_method
    def teachers(self, db: Session):
        return [
            db.query(Teacher).filter(Teacher.id == item.teacher_id).first()
            for item in db.query(LessonTeacher)
            .filter(LessonTeacher.lesson_id == self.id)
            .all()
        ]

    @hybrid_method
    def groups(self, db: Session):
        return [
            item.group_name
            for item in db.query(Lesson)
            .filter(
                Lesson.time_start == self.time_start,
                Lesson.time_end == self.time_end,
                Lesson.weeks == self.weeks,
                Lesson.date_start == self.date_start,
                Lesson.date_end == self.date_end,
                Lesson.day == self.day,
                Lesson.name == self.name,
            )
            .all()
        ]

    @hybrid_method
    def __eq__(self, other):
        return self.time_start == other.time_start and\
               self.time_end == other.time_end and\
               collections.Counter(self.weeks) == collections.Counter(other.weeks) and\
               self.name == other.name and\
               self.date_start == other.date_start and\
               self.date_end == other.date_end and\
               self.day == other.day

    @hybrid_method
    def __hash__(self):
        return hash(self.id)

    @hybrid_method
    def __repr__(self):
        return f"Model.Lesson({self.name}\n             {self.day}\n             {self.group_name}\n             {self.time_start}\n             {self.weeks}\n)"


class LessonTeacher(Base):
    __tablename__ = "lessons_teachers"

    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))

    __table_args__ = (
        PrimaryKeyConstraint(lesson_id, teacher_id),
    )

    lesson = relationship("Lesson", back_populates="lesson_teacher")
    teacher = relationship("Teacher", back_populates="lesson_teacher")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    pathToPreview = Column(String(150), unique=True)
    pathToNews = Column(String(150), unique=True)
