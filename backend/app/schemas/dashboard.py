from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_applications: int
    applied_count: int
    interview_count: int
    response_rate: float
    pending_follow_ups: int
