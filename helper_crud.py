# helper_crud.py (Corrected)

from sqlalchemy.orm import Session
import models
import valid_schemas

# ===================================================================
# GENERIC HELPER (for simple, single-key nodes)
# ===================================================================
def get_or_create(db: Session, model, **kwargs):
    """
    Checks if an instance of a model with a simple key exists.
    If it exists, it returns the instance. If not, it creates it.
    This is best used for tables with a single, non-composite primary key.
    """
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        db.add(instance)
        return instance, True

# ===================================================================
# NODE HELPERS (These can still use the generic helper)
# ===================================================================
def create_sd_objective(db: Session, objective: valid_schemas.SD_ObjectiveCreate):
    db_obj, _ = get_or_create(db, models.SD_Objective, **objective.model_dump())
    return db_obj

def create_sdg_goal(db: Session, goal: valid_schemas.SDG_GoalCreate):
    db_obj, _ = get_or_create(db, models.SDG_Goal, **goal.model_dump())
    return db_obj

def create_sdg_target(db: Session, target: valid_schemas.SDG_TargetCreate):
    db_obj, _ = get_or_create(db, models.SDG_Target, **target.model_dump())
    return db_obj

def create_sdg_indicator(db: Session, indicator: valid_schemas.SDG_IndicatorCreate):
    db_obj, _ = get_or_create(db, models.SDG_Indicator, **indicator.model_dump())
    return db_obj

def create_practice_action(db: Session, action: valid_schemas.PracticeActionCreate):
    db_obj, _ = get_or_create(db, models.PracticeAction, **action.model_dump())
    return db_obj

def create_practice(db: Session, practice: valid_schemas.PracticeCreate):
    db_obj, _ = get_or_create(db, models.Practice, **practice.model_dump())
    return db_obj

def create_stakeholder_group(db: Session, group: valid_schemas.Stakeholder_GroupCreate):
    db_obj, _ = get_or_create(db, models.Stakeholder_Group, **group.model_dump())
    return db_obj

def create_stakeholder(db: Session, stakeholder: valid_schemas.StakeholderCreate):
    db_obj, _ = get_or_create(db, models.Stakeholder, **stakeholder.model_dump())
    return db_obj

def create_concern(db: Session, concern: valid_schemas.ConcernCreate):
    db_obj, _ = get_or_create(db, models.Concern, **concern.model_dump())
    return db_obj

# ===================================================================
# LINK HELPERS (Rewritten to be specific and avoid the TypeError)
# ===================================================================
def create_practice_to_target_link(db: Session, link: valid_schemas.PracticeToTargetLinkCreate):
    # Check if the link already exists using the composite primary key
    db_obj = db.query(models.PracticeToTargetLink).filter_by(
        practice_id=link.practice_id,
        target_id=link.target_id
    ).first()
    
    if not db_obj:
        # If it doesn't exist, create it using all the data from the Pydantic model
        db_obj = models.PracticeToTargetLink(**link.model_dump())
        db.add(db_obj)
    return db_obj

def create_practice_to_action_link(db: Session, link: valid_schemas.PracticeToActionLinkCreate):
    db_obj = db.query(models.PracticeToActionLink).filter_by(
        practice_id=link.practice_id,
        action_id=link.action_id
    ).first()
    
    if not db_obj:
        db_obj = models.PracticeToActionLink(**link.model_dump())
        db.add(db_obj)
    return db_obj

def create_stakeholder_to_concern_link(db: Session, link: valid_schemas.StakeholderToConcernLinkCreate):
    db_obj = db.query(models.StakeholderToConcernLink).filter_by(
        stakeholder_id=link.stakeholder_id,
        concern_id=link.concern_id
    ).first()

    if not db_obj:
        db_obj = models.StakeholderToConcernLink(**link.model_dump())
        db.add(db_obj)
    return db_obj

def create_concern_to_target_link(db: Session, link: valid_schemas.ConcernToTargetLinkCreate):
    db_obj = db.query(models.ConcernToTargetLink).filter_by(
        concern_id=link.concern_id,
        target_id=link.target_id
    ).first()

    if not db_obj:
        db_obj = models.ConcernToTargetLink(**link.model_dump())
        db.add(db_obj)
    return db_obj

def create_sd_objective_to_sdg_link(db: Session, link: valid_schemas.SDObjectiveToSDGLinkCreate):
    db_obj = db.query(models.SDObjectiveToSDGLink).filter_by(
        sd_objective_id=link.sd_objective_id,
        sdg_goal_id=link.sdg_goal_id
    ).first()

    if not db_obj:
        db_obj = models.SDObjectiveToSDGLink(**link.model_dump())
        db.add(db_obj)
    return db_obj


# ==========================================================
# ===== NEW HELPERS FOR MINING PROJECT-LEVEL INDICATORS ============
# ==========================================================

def create_mining_indicator(db: Session, indicator: valid_schemas.MiningIndicatorCreate):
    """Creates a Mining Project Indicator, using its own ID from the CSV."""
    db_obj = db.query(models.MiningIndicator).filter(models.MiningIndicator.id == indicator.id).first()
    if not db_obj:
        db_obj = models.MiningIndicator(**indicator.model_dump())
        db.add(db_obj)
    return db_obj

def create_mining_indicator_to_target_link(db: Session, link: valid_schemas.MiningIndicatorToTargetLinkCreate):
    """Creates a link between a Mining Project Indicator and an SDG Target."""
    db_obj = db.query(models.MiningIndicatorToTargetLink).filter_by(
        mining_indicator_id=link.mining_indicator_id,
        target_id=link.target_id
    ).first()
    if not db_obj:
        db_obj = models.MiningIndicatorToTargetLink(**link.model_dump())
        db.add(db_obj)
    return db_obj

def create_practice_to_mining_indicator_link(db: Session, link: valid_schemas.PracticeToMiningIndicatorLinkCreate):
    """Creates a link between a Practice and a Mining Project Indicator."""
    db_obj = db.query(models.PracticeToMiningIndicatorLink).filter_by(
        practice_id=link.practice_id,
        mining_indicator_id=link.mining_indicator_id
    ).first()
    if not db_obj:
        db_obj = models.PracticeToMiningIndicatorLink(**link.model_dump())
        db.add(db_obj)
    return db_obj


print("✅ CRUD Helper functions defined and ready for use.")


# ===================================================================
# ===== END OF CRUD HELPER FUNCTIONS FOR MAMODA WEB DASHBOARD =========




# ================= Archvived Code ===========================

# def create_practice_action(db: Session, action: valid_schemas.PracticeActionCreate):
#     """
#     Creates a PracticeAction using the string-based ID from the CSV file.
#     """
#     # First, check if an object with this ID already exists.
#     db_obj = db.query(models.PracticeAction).filter(models.PracticeAction.id == action.id).first()
    
#     # If it doesn't exist, create it using all data from the Pydantic object.
#     if not db_obj:
#         # The action.model_dump() will include the 'id', 'name', and 'description'.
#         db_obj = models.PracticeAction(**action.model_dump())
#         db.add(db_obj)
        
#     return db_obj