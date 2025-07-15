from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Assuming your models.py file is in the same directory
# and contains the LevelEnum definition.
from models import LevelEnum

# ===================================================================
# BASE & CREATE SCHEMAS
# These schemas define the data structure for creating new records.
# They are used to validate incoming data before it touches the database.
# ===================================================================

# --- Node Schemas ---
class SD_ObjectiveBase(BaseModel):
    id: str
    description: str

class SDG_GoalBase(BaseModel):
    id: str
    name: str
    parent_objective_id: Optional[str] = None

class SDG_TargetBase(BaseModel):
    id: str
    short_name: str
    description: str
    parent_goal_id: str

class SDG_IndicatorBase(BaseModel):
    id: str
    description: str
    code: str
    parent_target_id: str


# --- Schemas for PracticeAction ---
class PracticeActionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PracticeBase(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    remark: Optional[str] = None
    evidence_source: Optional[str] = None 
    capital_intensity: Optional[LevelEnum] = None
    technical_complexity: Optional[LevelEnum] = None
    operational_disruption: Optional[LevelEnum] = None
    long_term_liability: Optional[bool] = None


class Stakeholder_GroupBase(BaseModel):
    id: str
    name: str
    evidence: Optional[str] = None
    description: Optional[str] = None

class StakeholderBase(BaseModel):
    id: str
    name: str
    category_id: str
    definition: Optional[str] = None
    description: Optional[str] = None
    evidence: Optional[str] = None

class ConcernBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    evidence: Optional[str] = None

# --- Link Schemas ---

class PracticeToTargetLinkBase(BaseModel):
    practice_id: str
    target_id: str
    relevance_weight: LevelEnum
    is_direct: bool
    evidence: Optional[str] = None
    math_model: Optional[str] = None

class PracticeToActionLinkBase(BaseModel):
    practice_id: str
    action_id: int
    evidence: Optional[str] = None

class StakeholderToConcernLinkBase(BaseModel):
    stakeholder_id: str
    concern_id: str
    priority_weight: LevelEnum
    evidence: Optional[str] = None

class ConcernToTargetLinkBase(BaseModel):
    concern_id: str
    target_id: str
    evidence: Optional[str] = None

class SDObjectiveToSDGLinkBase(BaseModel):
    sd_objective_id: str
    sdg_goal_id: str
    weight: LevelEnum
    comment: Optional[str] = None
    # UPDATED: Added evidence field to match the model
    evidence: Optional[str] = None

# --- Aliasing Create schemas ---
# We create aliases for clarity. The 'Create' schema is what we expect
# as input when creating a new entry in the database.
SD_ObjectiveCreate = SD_ObjectiveBase
SDG_GoalCreate = SDG_GoalBase
SDG_TargetCreate = SDG_TargetBase
SDG_IndicatorCreate = SDG_IndicatorBase
PracticeActionCreate = PracticeActionBase
PracticeCreate = PracticeBase
Stakeholder_GroupCreate = Stakeholder_GroupBase
StakeholderCreate = StakeholderBase
ConcernCreate = ConcernBase
PracticeToTargetLinkCreate = PracticeToTargetLinkBase
PracticeToActionLinkCreate = PracticeToActionLinkBase
StakeholderToConcernLinkCreate = StakeholderToConcernLinkBase
ConcernToTargetLinkCreate = ConcernToTargetLinkBase
SDObjectiveToSDGLinkCreate = SDObjectiveToSDGLinkBase


# ===================================================================
# READ SCHEMAS
# These schemas are used when reading data from the database.
# They include relationships to other objects and are configured to
# work with SQLAlchemy's ORM objects.
# ===================================================================

# --- Link Read Schemas ---
class PracticeToActionLinkRead(PracticeToActionLinkBase):    # action: PracticeActionRead
    class Config:
        from_attributes = True

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
# The order of these classes is important to avoid forward reference issues.
# A class must be defined before it is referenced as a nested type in another class.

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

class PracticeActionRead(PracticeActionBase):
    id: int
    class Config:
        from_attributes = True

class PracticeRead(PracticeBase):
    target_links: List[PracticeToTargetLinkRead] = []
    action_links: List[PracticeToActionLinkRead] = []
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