import enum


class TaskStatus(enum.StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(enum.StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProjectStatus(enum.StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
