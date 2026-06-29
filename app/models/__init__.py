"""
Imports every model so Alembic's autogenerate and Base.metadata
can discover all tables. Without this, `alembic revision --autogenerate`
will silently miss any model not imported somewhere before it runs.
"""
from app.models.user import User, UserRole
from app.models.customer_profile import CustomerProfile
from app.models.fundi_profile import FundiProfile
from app.models.category import Category
from app.models.fundi_category import FundiCategory
from app.models.job import Job, JobStatus
from app.models.job_assignment import JobAssignment
from app.models.invoice import Invoice, InvoiceStatus
from app.models.review import Review
from app.models.platform_setting import PlatformSetting
from app.models.notification import Notification

__all__ = [
    "User", "UserRole",
    "CustomerProfile",
    "FundiProfile",
    "Category",
    "FundiCategory",
    "Job", "JobStatus",
    "JobAssignment",
    "Invoice", "InvoiceStatus",
    "Review",
    "PlatformSetting",
    "Notification",
]