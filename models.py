from pydantic import BaseModel, Field
from typing import Optional

class College(BaseModel):
    _id: str
    name: str
    status: Optional[str]
    district: Optional[str]
    region: Optional[str]

class Course(BaseModel):
    _id: Optional[str]
    branch_name: str

class Cutoff(BaseModel):
    _id: Optional[str]
    college_id: str
    choice_code: str
    branch_name: str
    academic_year: str
    cap_round: Optional[int]
    seat_type: Optional[str]
    caste_category: Optional[str]
    gender: Optional[str]
    state_merit_rank: Optional[int]
    cutoff_percentage: Optional[float]
    admission_stage: Optional[str]
