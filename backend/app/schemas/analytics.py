from typing import List, Dict
from pydantic import BaseModel

class CategoryDistributionItem(BaseModel):
    category_name: str
    count: int

class LocationDistributionItem(BaseModel):
    building_name: str
    count: int

class PriorityDistributionItem(BaseModel):
    priority: str
    count: int

class StaffWorkloadItem(BaseModel):
    staff_id: str
    staff_name: str
    assigned_count: int
    in_progress_count: int
    resolved_count: int

class AnalyticsKPIResponse(BaseModel):
    total_complaints: int
    open_complaints: int
    assigned_complaints: int
    in_progress_complaints: int
    resolved_complaints: int
    closed_complaints: int
    rejected_complaints: int
    sla_breached_complaints: int
    avg_resolution_time_hours: float
    resolution_rate_percent: float

class AnalyticsDashboardResponse(BaseModel):
    kpi: AnalyticsKPIResponse
    by_category: List[CategoryDistributionItem]
    by_location: List[LocationDistributionItem]
    by_priority: List[PriorityDistributionItem]
    staff_workload: List[StaffWorkloadItem]
