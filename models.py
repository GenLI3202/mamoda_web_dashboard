# sqlalchemy imports for database schema definition
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    Enum as SQLAlchemyEnum # Renamed to avoid conflict with Python's Enum
)

# sqlalchemy.orm imports for object-relational mapping
from sqlalchemy.orm import relationship, declarative_base

# Python's built-in enum for creating controlled vocabularies
from enum import Enum

# This Enum provides controlled vocabulary for certain model fields.
# Using a standard Python Enum is good practice and can be used by other parts
# of the application (like Pydantic models or frontend components).
class LevelEnum(Enum):
    HIGH = 'H'
    HIGH_MEDIUM = 'H/M'
    MEDIUM = 'M'
    MEDIUM_LOW = 'M/L'
    LOW = 'L'


# The Declarative Base is a factory for creating base classes for your ORM models.
# All of our model classes will inherit from this 'Base' object.
# SQLAlchemy's machinery will then map these classes to tables in the database.
Base = declarative_base()



####################### Define the Entities (Nodes) #######################

class SD_Objective(Base):
    __tablename__ = 'sd_objectives'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "Env", "Soc", "Econ"
    
    # Relationships
    # This defines the one-to-many relationship from SD_Objective to SDG_Goal.
    # The 'back_populates' argument creates a two-way linkage, connecting to the 'objective' attribute in the SDG_Goal class.
    sdg_goals = relationship("SDG_Goal", back_populates="objective")

    def __repr__(self):
        return f"<SD_Objective(id='{self.id}')>"
    
class SDG_Goal(Base):
    __tablename__ = 'sdg_goal'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "SDG1"
    name = Column(String, nullable=False)
    parent_objective_id = Column(String, ForeignKey('sd_objectives.id'))
    
    # Relationships
    # Many-to-one relationship back to SD_Objective
    objective = relationship("SD_Objective", back_populates="sdg_goals")
    # One-to-many relationship to SDG_Target
    targets = relationship("SDG_Target", back_populates="goal")

    def __repr__(self):
        return f"<SDG_Goal(id='{self.id}', name='{self.name}')>"
    
class Practice(Base):
    __tablename__ = 'practice'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "p1"
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text)
    major_actions_involved = Column(Text)
    remark = Column(Text)
    evidence_source = Column(Text, nullable=True)    
    
    # Using the 5-level Enum for qualitative assessment
    capital_intensity = Column(SQLAlchemyEnum(LevelEnum))
    technical_complexity = Column(SQLAlchemyEnum(LevelEnum))
    operational_disruption = Column(SQLAlchemyEnum(LevelEnum))
    
    # Boolean for true/false values
    long_term_liability = Column(Boolean)
    
    # Relationships
    # This will link to the PracticeToTargetLink association object.
    target_links = relationship("PracticeToTargetLink", back_populates="practice")

    def __repr__(self):
        return f"<Practice(id='{self.id}', name='{self.name}')>"
    

class SDG_Target(Base):
    __tablename__ = 'sdg_target'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "1.1"
    description = Column(Text, nullable=False)
    parent_goal_id = Column(String, ForeignKey('sdg_goal.id'))
    
    # Relationships
    # Many-to-one relationship back to its parent goal
    goal = relationship("SDG_Goal", back_populates="targets")
    # One-to-many relationship to its indicators
    indicators = relationship("SDG_Indicator", back_populates="target")
    # Link to association objects for many-to-many relationships
    practice_links = relationship("PracticeToTargetLink", back_populates="target")
    concern_links = relationship("ConcernToTargetLink", back_populates="target")

    def __repr__(self):
        return f"<SDG_Target(id='{self.id}')>"

class SDG_Indicator(Base):
    __tablename__ = 'sdg_indicator'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "1.1.1"
    description = Column(Text, nullable=False)
    code = Column(String)
    parent_target_id = Column(String, ForeignKey('sdg_target.id'))
    
    # Relationships
    # Many-to-one relationship back to its parent target
    target = relationship("SDG_Target", back_populates="indicators")

    def __repr__(self):
        return f"<SDG_Indicator(id='{self.id}')>"
    
class Stakeholder_Group(Base):
    __tablename__ = 'stakeholder_group'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "shg1_cv_sct"
    name = Column(String, nullable=False)
    
    # Relationships
    # One-to-many relationship to the Stakeholder class
    evidence = Column(Text, nullable=True)    
    stakeholders = relationship("Stakeholder", back_populates="group")
    
    def __repr__(self):
        return f"<Stakeholder_Group(id='{self.id}', name='{self.name}')>"

class Stakeholder(Base):
    __tablename__ = 'stakeholder'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "sh1"
    name = Column(String, nullable=False)
    category_id = Column(String, ForeignKey('stakeholder_group.id'))
    definition = Column(Text)
    description = Column(Text)
    
    # Relationships
    # Many-to-one relationship back to its group
    evidence = Column(Text, nullable=True)    
    group = relationship("Stakeholder_Group", back_populates="stakeholders")
    # One-to-many relationship to the association object
    concern_links = relationship("StakeholderToConcernLink", back_populates="stakeholder")

    def __repr__(self):
        return f"<Stakeholder(id='{self.id}', name='{self.name}')>"

class Concern(Base):
    __tablename__ = 'concern'
    
    # Columns
    id = Column(String, primary_key=True) # E.g., "concern_jobs"
    name = Column(String, nullable=False)
    description = Column(Text)
    evidence = Column(Text, nullable=True)    
    # Relationships
    # These will link to our association objects, which we'll define in Part 3.
    sh_links = relationship("StakeholderToConcernLink", back_populates="concern")
    target_links = relationship("ConcernToTargetLink", back_populates="concern")
    
    def __repr__(self):
        return f"<Concern(id='{self.id}', name='{self.name}')>"




######################### Define the Association Objects (Links/Edges) #######################


# Import the current time function for the last_updated default
from datetime import datetime, timezone

class PracticeToTargetLink(Base):
    __tablename__ = 'practice_to_target_link'
    
    # Composite primary key made of two foreign keys
    practice_id = Column(String, ForeignKey('practice.id'), primary_key=True)
    target_id = Column(String, ForeignKey('sdg_target.id'), primary_key=True)
    
    # Attributes specific to the link
    relevance_weight = Column(SQLAlchemyEnum(LevelEnum), nullable=False)
    is_direct = Column(Boolean, nullable=False)
    evidence = Column(Text)
    math_model = Column(Text)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships to navigate back to the parent objects
    # These connect to the 'target_links' attribute in the Practice class
    # and the 'practice_links' attribute in the SDG_Target class.
    practice = relationship("Practice", back_populates="target_links")
    target = relationship("SDG_Target", back_populates="practice_links")

    def __repr__(self):
        return f"<PracticeToTargetLink practice='{self.practice_id}' target='{self.target_id}'>"
    

class StakeholderToConcernLink(Base):
    __tablename__ = 'stakeholder_to_concern_link'
    
    # Composite primary key
    stakeholder_id = Column(String, ForeignKey('stakeholder.id'), primary_key=True)
    concern_id = Column(String, ForeignKey('concern.id'), primary_key=True)
    
    # Attributes specific to the link
    priority_weight = Column(SQLAlchemyEnum(LevelEnum), nullable=False)
    evidence = Column(Text)
    
    # Relationships for back-population
    stakeholder = relationship("Stakeholder", back_populates="concern_links")
    concern = relationship("Concern", back_populates="sh_links")

    def __repr__(self):
        return f"<StakeholderToConcernLink stakeholder='{self.stakeholder_id}' concern='{self.concern_id}'>"


class ConcernToTargetLink(Base):
    __tablename__ = 'concern_to_target_link'
    
    # Composite primary key
    concern_id = Column(String, ForeignKey('concern.id'), primary_key=True)
    target_id = Column(String, ForeignKey('sdg_target.id'), primary_key=True)
    evidence = Column(Text, nullable=True)    
    # Relationships for back-population
    concern = relationship("Concern", back_populates="target_links")
    target = relationship("SDG_Target", back_populates="concern_links")

    def __repr__(self):
        return f"<ConcernToTargetLink concern='{self.concern_id}' target='{self.target_id}'>"

class SDObjectiveToSDGLink(Base):
    __tablename__ = 'sd_objective_to_sdg_link'

    # Composite primary key
    sd_objective_id = Column(String, ForeignKey('sd_objectives.id'), primary_key=True)
    sdg_goal_id = Column(String, ForeignKey('sdg_goal.id'), primary_key=True)
    evidence = Column(Text, nullable=True)    

    # Attributes specific to the link
    # We use our 5-level enum here for consistency
    weight = Column(SQLAlchemyEnum(LevelEnum), nullable=False)
    comment = Column(Text)
    
    # Note: we are defining this table to store properties about the link itself. 
    # We are omitting the direct relationship() attributes here to avoid conflicting 
    # with the simpler one-to-many relationship already defined between
    # SD_Objective and SDG_Goal. This table acts as an "enrichment" layer.

    def __repr__(self):
        return f"<SDObjectiveToSDGLink objective='{self.sd_objective_id}' goal='{self.sdg_goal_id}'>"   