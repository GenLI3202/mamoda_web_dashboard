from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Assuming your models.py file is in the same directory
# and contains the LevelEnum definition.
from models import LevelEnum

# ===================================================================
# BASE & CREATE SCHEMAS
# (These remain unchanged)
# ===================================================================

# --- Node Schemas ---
class SD_ObjectiveBase(BaseModel):
    id: str

class SDG_GoalBase(BaseModel):
    id: str
    name: str
    parent_objective_id: str

class SDG_TargetBase(BaseModel):
    id: str
    description: str
    parent_goal_id: str

class SDG_IndicatorBase(BaseModel):
    id: str
    description: str
    code: Optional[str] = None
    parent_target_id: str

class PracticeBase(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    major_actions_involved: Optional[str] = None
    remark: Optional[str] = None
    evidence_source: Optional[str] = None
    capital_intensity: Optional[LevelEnum] = None
    technical_complexity: Optional[LevelEnum] = None
    operational_disruption: Optional[LevelEnum] = None
    long_term_liability: Optional[bool] = None

class Stakeholder_GroupBase(BaseModel):
    id: str
    name: str

class StakeholderBase(BaseModel):
    id: str
    name: str
    category_id: str
    definition: Optional[str] = None
    description: Optional[str] = None

class ConcernBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

# --- Link Schemas ---
class PracticeToTargetLinkBase(BaseModel):
    practice_id: str
    target_id: str
    relevance_weight: LevelEnum
    is_direct: bool
    evidence: Optional[str] = None
    math_model: Optional[str] = None

class StakeholderToConcernLinkBase(BaseModel):
    stakeholder_id: str
    concern_id: str
    priority_weight: LevelEnum
    evidence: Optional[str] = None

class ConcernToTargetLinkBase(BaseModel):
    concern_id: str
    target_id: str

class SDObjectiveToSDGLinkBase(BaseModel):
    sd_objective_id: str
    sdg_goal_id: str
    weight: LevelEnum
    comment: Optional[str] = None

# --- Aliasing Create schemas ---
SD_ObjectiveCreate = SD_ObjectiveBase
SDG_GoalCreate = SDG_GoalBase
SDG_TargetCreate = SDG_TargetBase
SDG_IndicatorCreate = SDG_IndicatorBase
PracticeCreate = PracticeBase
Stakeholder_GroupCreate = Stakeholder_GroupBase
StakeholderCreate = StakeholderBase
ConcernCreate = ConcernBase
PracticeToTargetLinkCreate = PracticeToTargetLinkBase
StakeholderToConcernLinkCreate = StakeholderToConcernLinkBase
ConcernToTargetLinkCreate = ConcernToTargetLinkBase
SDObjectiveToSDGLinkCreate = SDObjectiveToSDGLinkBase


# ===================================================================
# READ SCHEMAS 
# These are used for data output and include relationships.
# They have from_attributes = True to read from SQLAlchemy models.
# ===================================================================

# --- Link Read Schemas ---
class PracticeToTargetLinkRead(PracticeToTargetLinkBase):
    last_updated: datetime
    class Config:
        from_attributes = True

class StakeholderToConcernLinkRead(StakeholderToConcernLinkBase):
    class Config:
        from_attributes = True

class ConcernToTargetLinkRead(ConcernToTargetLinkBase):
    class Config:
        from_attributes = True

class SDObjectiveToSDGLinkRead(SDObjectiveToSDGLinkBase):
    class Config:
        from_attributes = True

# --- Node Read Schemas ---
# The order here is important to help with forward references

class SDG_IndicatorRead(SDG_IndicatorBase):
    class Config:
        from_attributes = True

class SDG_TargetRead(SDG_TargetBase):
    # This now includes its indicators and maintains the other links
    indicators: List[SDG_IndicatorRead] = []
    practice_links: List[PracticeToTargetLinkRead] = []
    concern_links: List[ConcernToTargetLinkRead] = []
    class Config:
        from_attributes = True

class SDG_GoalRead(SDG_GoalBase):
    # This now includes the list of its targets
    targets: List[SDG_TargetRead] = []
    class Config:
        from_attributes = True

class SD_ObjectiveRead(SD_ObjectiveBase):
    # This now includes the list of its SDG goals
    sdg_goals: List[SDG_GoalRead] = []
    class Config:
        from_attributes = True

class PracticeRead(PracticeBase):
    target_links: List[PracticeToTargetLinkRead] = []
    class Config:
        from_attributes = True

class ConcernRead(ConcernBase):
    sh_links: List[StakeholderToConcernLinkRead] = []
    target_links: List[ConcernToTargetLinkRead] = []
    class Config:
        from_attributes = True

class StakeholderRead(StakeholderBase):
    concern_links: List[StakeholderToConcernLinkRead] = []
    class Config:
        from_attributes = True

class Stakeholder_GroupRead(Stakeholder_GroupBase):
    # This now includes the list of stakeholders in the group
    stakeholders: List[StakeholderRead] = []
    class Config:
        from_attributes = True

