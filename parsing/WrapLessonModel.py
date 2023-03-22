class WrapLessonModel:
    lesson: LessonModel
    groups: set
    teachers: set
    rooms: str

    def __init__(self,
                 lesson: LessonModel,
                 groups: set,
                 teachers: set,
                 rooms: str,
                 ):
        self.lesson = lesson
        self.groups = groups
        self.teachers = set()
        self.teachers.update(teachers)
        self.rooms = rooms

    def __repr__(self):
        return f'lesson: {self.lesson.trans[0].name},\n' \
               f'groups: {self.groups},\n' \
               f'teachers: {self.teachers},\n' \
               f'rooms: {self.rooms}\n\n'

    def __eq__(self, other):
        if type(other) is type(self):
            return (self.lesson.time_start == other.lesson.time_start and
                    self.lesson.time_end == other.lesson.time_end and
                    self.lesson.dot == other.lesson.dot and
                    self.lesson.weeks == other.lesson.weeks and
                    self.lesson.date_start == other.lesson.date_start and
                    self.lesson.date_end == other.lesson.date_end and
                    self.lesson.day == other.lesson.day and
                    self.rooms == other.rooms and
                    self.lesson.trans[0].name == other.lesson.trans[0].name and
                    self.lesson.trans[0].subgroup == other.lesson.trans[0].subgroup and
                    self.lesson.trans[0].type == other.lesson.trans[0].type and
                    self.lesson.trans[0].lang == other.lesson.trans[0].lang)

    def __hash__(self):
        self_trans = [str(tr.name) + str(tr.subgroup) + str(tr.lang) + str(tr.type) for tr in self.lesson.trans]
        return hash(
            str(self.lesson.time_start) + str(self.lesson.time_end) + str(self.lesson.dot) + str(self.lesson.weeks)
            + str(self.lesson.date_start) + str(self.lesson.date_end) + str(self.lesson.day) + str(self.rooms) +
            "".join(self_trans))