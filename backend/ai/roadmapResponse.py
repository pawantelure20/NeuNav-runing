from pydantic import BaseModel, HttpUrl
from typing import List, Literal


class WeeklyPlan(BaseModel):
    week: int
    plan: str


class Timeline(BaseModel):
    level: Literal["beginner", "intermediate", "advanced"]
    phase_content: str
    weekly_breakdown: List[WeeklyPlan]


class RoadmapResponse(BaseModel):
    overview: str
    strategies: List[str]
    resources: List[str]
    timeline: Timeline
    references: List[HttpUrl]