from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from neo4j import GraphDatabase

# ----------------------------
# Database connection
# ----------------------------
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ----------------------------
# Pydantic models (schemas)
# ----------------------------
class DataSource(BaseModel):
    LastCatalogUpdate: Optional[str]
    UniqueId: Optional[int]
    PublicData: Optional[bool]
    Name: Optional[str]

class SpaceObjectRoot(BaseModel):
    CatalogId: Optional[str]

# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(title="Neo4j Graph REST API")

# ----------------------------
# Helper functions
# ----------------------------
def run_query(query: str, parameters: dict = {}) -> List[Any]:
    with driver.session() as session:
        result = session.run(query, parameters)
        return [record.data() for record in result]

# ----------------------------
# CRUD for DataSource
# ----------------------------
@app.get("/datasources", response_model=List[DataSource])
def list_datasources(
    Name: Optional[str] = Query(None),
    UniqueId_gte: Optional[int] = Query(None)
):
    query = "MATCH (d:DataSource) WHERE 1=1 "
    params = {}

    if Name:
        query += "AND d.Name = $Name "
        params["Name"] = Name
    if UniqueId_gte is not None:
        query += "AND d.UniqueId >= $UniqueId_gte "
        params["UniqueId_gte"] = UniqueId_gte

    query += "RETURN d"
    results = run_query(query, params)
    return [r["d"] for r in results]

@app.get("/datasources/{id}", response_model=DataSource)
def get_datasource(id: str):
    query = "MATCH (d:DataSource {Name: $id}) RETURN d"
    results = run_query(query, {"id": id})
    if not results:
        raise HTTPException(status_code=404, detail="DataSource not found")
    return results[0]["d"]

@app.post("/datasources", response_model=DataSource)
def create_datasource(ds: DataSource):
    query = """
    CREATE (d:DataSource {LastCatalogUpdate:$LastCatalogUpdate, UniqueId:$UniqueId, PublicData:$PublicData, Name:$Name})
    RETURN d
    """
    results = run_query(query, ds.dict(exclude_none=True))
    return results[0]["d"]

@app.patch("/datasources/{id}", response_model=DataSource)
def update_datasource(id: str, ds: DataSource):
    updates = {k: v for k, v in ds.dict().items() if v is not None}
    set_clause = ", ".join([f"d.{k} = ${k}" for k in updates])
    query = f"""
    MATCH (d:DataSource {{Name:$id}})
    SET {set_clause}
    RETURN d
    """
    params = {"id": id, **updates}
    results = run_query(query, params)
    if not results:
        raise HTTPException(status_code=404, detail="DataSource not found")
    return results[0]["d"]

@app.delete("/datasources/{id}")
def delete_datasource(id: str):
    query = "MATCH (d:DataSource {Name:$id}) DETACH DELETE d"
    run_query(query, {"id": id})
    return {"status": "deleted"}

# ----------------------------
# Relationship example
# ----------------------------
@app.get("/datasources/{id}/spaceobjectroots", response_model=List[SpaceObjectRoot])
def get_datasource_spaceobjectroots(id: str):
    query = """
    MATCH (d:DataSource {Name:$id})-[:has_catalog]->(s:SpaceObjectRoot)
    RETURN s
    """
    results = run_query(query, {"id": id})
    return [r["s"] for r in results]
