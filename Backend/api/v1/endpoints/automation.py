"""
Automation endpoints for workflows, templates, and logs.

In-memory store suitable for development; safe to call without DB.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter()


class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    status: str = "active"  # active|paused
    triggers: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    last_run: Optional[str] = None
    next_run: Optional[str] = None


class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: str
    description: str
    usage: int = 0
    last_used: Optional[str] = None


class RunLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow: str
    status: str  # success|error
    time: str
    duration: str


_workflows: Dict[str, Workflow] = {}
_templates: Dict[str, Template] = {}
_logs: List[RunLog] = []


@router.get("/workflows")
async def list_workflows() -> Dict[str, Any]:
    return {"items": list(_workflows.values())}


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str
    trigger: Optional[str] = None
    action: Optional[str] = None


@router.post("/workflows")
async def create_workflow(body: CreateWorkflowRequest) -> Workflow:
    wf = Workflow(
        name=body.name,
        description=body.description,
        status="active",
        triggers=[body.trigger] if body.trigger else [],
        actions=[body.action] if body.action else [],
        last_run="Never",
        next_run="Pending",
    )
    _workflows[wf.id] = wf
    return wf


@router.post("/workflows/{workflow_id}/toggle")
async def toggle_workflow(workflow_id: str) -> Dict[str, Any]:
    wf = _workflows.get(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.status = "paused" if wf.status == "active" else "active"
    _workflows[workflow_id] = wf
    return {"success": True, "status": wf.status}


@router.post("/workflows/{workflow_id}/run")
async def run_workflow(workflow_id: str) -> Dict[str, Any]:
    wf = _workflows.get(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    # Simulate a run
    log = RunLog(
        workflow=wf.name,
        status="success",
        time=f"{datetime.utcnow().isoformat()}Z",
        duration="45s",
    )
    _logs.insert(0, log)
    wf.last_run = "Just now"
    wf.next_run = "In 4 hours"
    _workflows[workflow_id] = wf
    return {"success": True, "log_id": log.id}


@router.get("/templates")
async def list_templates() -> Dict[str, Any]:
    return {"items": list(_templates.values())}


@router.get("/logs")
async def list_logs() -> Dict[str, Any]:
    return {"items": _logs[:50]}


