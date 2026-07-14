"""Job lifecycle values shared by all interfaces."""

from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    PREPARING = "preparing"
    RUNNING = "running"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed-with-warnings"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
