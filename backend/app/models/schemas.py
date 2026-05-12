from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

FeatureName = Literal[
    "aiops",
    "finops_cost_analytics",
    "inventory_management",
    "log_analytics_agent",
    "os_management",
]

RunState = Literal["queued", "running", "completed"]


class Credentials(BaseModel):
    email: str
    password: str
    mfa_code: Optional[str] = None


class Workspace(BaseModel):
    business: Optional[str] = None
    environment: Optional[str] = None
    cloud_provider: Optional[str] = None
    account: Optional[str] = None


class RunE2ERequest(BaseModel):
    base_url: str = Field(default="https://beta.codly.ai")
    credentials: Credentials
    workspace: Workspace


class FeatureResult(BaseModel):
    feature: FeatureName
    status: Literal["pending", "running", "passed", "failed", "skipped"]
    message: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    artifacts: Dict[str, str] = {}


class RunStatus(BaseModel):
    run_id: str
    state: RunState
    current_feature: Optional[FeatureName] = None
    features: List[FeatureResult]
    created_at: str
    finished_at: Optional[str] = None