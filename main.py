# FILE: main.py

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Import all specific model classes from your models.py file
from models import (
    Base, Practice, Stakeholder, Concern, SDG_Target, SDG_Goal,
    SD_Objective, PracticeAction, Stakeholder_Group, MiningIndicator,
    PracticeToTargetLink, StakeholderToConcernLink, ConcernToTargetLink,
    PracticeToActionLink, MiningIndicatorToTargetLink, PracticeToMiningIndicatorLink,
    SDObjectiveToSDGLink
)

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./mining_knowledge.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- FASTAPI APP ---
app = FastAPI()

# --- HELPER FUNCTION ---
def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

# --- API ENDPOINTS ---

@app.get("/api/tables")
def get_table_names():
    inspector = inspect(engine)
    return inspector.get_table_names()

@app.get("/api/table/{table_name}")
def get_table_data(table_name: str):
    db = SessionLocal()
    try:
        ModelClass = next((m.class_ for m in Base.registry.mappers if m.local_table.name == table_name), None)
        if not ModelClass:
            raise HTTPException(status_code=404, detail="Table not found")
        records = db.query(ModelClass).all()
        return [object_as_dict(rec) for rec in records]
    finally:
        db.close()

# --- FULLY CORRECTED ENDPOINT FOR KNOWLEDGE GRAPH ---
@app.get("/api/graph-data")
def get_graph_data():
    """
    This endpoint queries ALL tables from models.py and formats the data
    into a structure that vis.js can understand: a list of nodes and a list of edges.
    """
    db = SessionLocal()
    try:
        # 1. Fetch all entity data to create the NODES
        nodes = []
        
        # Node types are added one by one for clarity
        nodes.extend([{'id': p.id, 'label': p.name, 'group': 'practice'} for p in db.query(Practice).all()])
        nodes.extend([{'id': s.id, 'label': s.name, 'group': 'stakeholder'} for s in db.query(Stakeholder).all()])
        nodes.extend([{'id': c.id, 'label': c.name, 'group': 'concern'} for c in db.query(Concern).all()])
        nodes.extend([{'id': t.id, 'label': t.short_name, 'group': 'target'} for t in db.query(SDG_Target).all()])
        nodes.extend([{'id': g.id, 'label': g.name, 'group': 'goal'} for g in db.query(SDG_Goal).all()])
        nodes.extend([{'id': o.id, 'label': o.id, 'group': 'objective'} for o in db.query(SD_Objective).all()])
        nodes.extend([{'id': a.id, 'label': a.name, 'group': 'action'} for a in db.query(PracticeAction).all()])
        nodes.extend([{'id': sg.id, 'label': sg.name, 'group': 'stakeholder_group'} for sg in db.query(Stakeholder_Group).all()])
        nodes.extend([{'id': mi.id, 'label': mi.name, 'group': 'indicator'} for mi in db.query(MiningIndicator).all()])

        # 2. Fetch all link data to create the EDGES, using the correct column names
        edges = []
        
        # Link types are added one by one for clarity
        edges.extend([{'from': l.practice_id, 'to': l.target_id} for l in db.query(PracticeToTargetLink).all()])
        edges.extend([{'from': l.stakeholder_id, 'to': l.concern_id} for l in db.query(StakeholderToConcernLink).all()])
        edges.extend([{'from': l.concern_id, 'to': l.target_id} for l in db.query(ConcernToTargetLink).all()])
        edges.extend([{'from': l.practice_id, 'to': l.action_id} for l in db.query(PracticeToActionLink).all()])
        edges.extend([{'from': l.mining_indicator_id, 'to': l.target_id} for l in db.query(MiningIndicatorToTargetLink).all()])
        edges.extend([{'from': l.practice_id, 'to': l.mining_indicator_id} for l in db.query(PracticeToMiningIndicatorLink).all()])
        edges.extend([{'from': l.sd_objective_id, 'to': l.sdg_goal_id} for l in db.query(SDObjectiveToSDGLink).all()])

        # Add edges from foreign keys defined directly on the models
        for target in db.query(SDG_Target).all():
            if target.parent_goal_id: edges.append({'from': target.id, 'to': target.parent_goal_id})
        for goal in db.query(SDG_Goal).all():
            if goal.parent_objective_id: edges.append({'from': goal.id, 'to': goal.parent_objective_id})
        for stakeholder in db.query(Stakeholder).all():
            if stakeholder.category_id: edges.append({'from': stakeholder.id, 'to': stakeholder.category_id})
        
        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        print(f"An error occurred in get_graph_data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching graph data.")
    finally:
        db.close()


# --- SERVE THE FRONTEND ---
app.mount("/", StaticFiles(directory=".", html=True), name="static")