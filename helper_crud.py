
# 1. Imports
from sqlalchemy.orm import Session
# It's good practice to import the modules themselves to maintain namespace clarity.
import models
import d_schemas

# 2. Generic get_or_create function
def get_or_create(db: Session, model, **kwargs):
    """
    Checks if an instance of a model exists in the database.
    If it exists, it returns the instance and False.
    If not, it creates a new instance, adds it to the session, and returns it and True.
    """
    # For models with composite keys, we filter by all primary key columns.
    # For others, we can just use the provided kwargs.
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False # Return instance and a flag indicating it was not created
    else:
        instance = model(**kwargs)
        db.add(instance)
        # Note: We don't commit here. The calling function is responsible for the commit.
        return instance, True # Return instance and a flag indicating it was created

# 3. Specific create functions for each model

# --- Node Helpers ---

def create_sd_objective(db: Session, objective: d_schemas.SD_ObjectiveCreate):
    db_obj, _ = get_or_create(db, models.SD_Objective, id=objective.id)
    return db_obj

def create_sdg_goal(db: Session, goal: d_schemas.SDG_GoalCreate):
    db_obj, _ = get_or_create(db, models.SDG_Goal, **goal.model_dump())
    return db_obj

def create_sdg_target(db: Session, target: d_schemas.SDG_TargetCreate):
    db_obj, _ = get_or_create(db, models.SDG_Target, **target.model_dump())
    return db_obj

def create_sdg_indicator(db: Session, indicator: d_schemas.SDG_IndicatorCreate):
    db_obj, _ = get_or_create(db, models.SDG_Indicator, **indicator.model_dump())
    return db_obj

def create_practice(db: Session, practice: d_schemas.PracticeCreate):
    db_obj, _ = get_or_create(db, models.Practice, **practice.model_dump())
    return db_obj

def create_stakeholder_group(db: Session, group: d_schemas.Stakeholder_GroupCreate):
    db_obj, _ = get_or_create(db, models.Stakeholder_Group, **group.model_dump())
    return db_obj

def create_stakeholder(db: Session, stakeholder: d_schemas.StakeholderCreate):
    db_obj, _ = get_or_create(db, models.Stakeholder, **stakeholder.model_dump())
    return db_obj

def create_concern(db: Session, concern: d_schemas.ConcernCreate):
    db_obj, _ = get_or_create(db, models.Concern, **concern.model_dump())
    return db_obj

# --- Link Helpers ---

def create_practice_to_target_link(db: Session, link: d_schemas.PracticeToTargetLinkCreate):
    # For link tables with composite keys, we filter by the primary key fields
    # to check for existence.
    db_obj, _ = get_or_create(
        db,
        models.PracticeToTargetLink,
        practice_id=link.practice_id,
        target_id=link.target_id,
        # If the link doesn't exist, the remaining data is used to create it.
        **link.model_dump()
    )
    return db_obj

def create_stakeholder_to_concern_link(db: Session, link: d_schemas.StakeholderToConcernLinkCreate):
    db_obj, _ = get_or_create(
        db,
        models.StakeholderToConcernLink,
        stakeholder_id=link.stakeholder_id,
        concern_id=link.concern_id,
        **link.model_dump()
    )
    return db_obj

def create_concern_to_target_link(db: Session, link: d_schemas.ConcernToTargetLinkCreate):
    db_obj, _ = get_or_create(
        db,
        models.ConcernToTargetLink,
        concern_id=link.concern_id,
        target_id=link.target_id,
        **link.model_dump()
    )
    return db_obj

def create_sd_objective_to_sdg_link(db: Session, link: d_schemas.SDObjectiveToSDGLinkCreate):
    db_obj, _ = get_or_create(
        db,
        models.SDObjectiveToSDGLink,
        sd_objective_id=link.sd_objective_id,
        sdg_goal_id=link.sdg_goal_id,
        **link.model_dump()
    )
    return db_obj


print("CRUD Helper functions defined and ready for use.")