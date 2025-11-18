"""
Pydantic models used for API serialization.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    user_id: str
    name: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None


class PolicyRuleModel(BaseModel):
    rule_id: str
    policy_profile_id: str
    rule_key: str
    description: str
    category: str
    expression: str
    severity: str
    auto_fixable: bool


class PolicyProfileModel(BaseModel):
    policy_profile_id: str
    name: str
    domain: str
    version: str
    created_at: datetime
    rules: List[PolicyRuleModel] = Field(default_factory=list)


class RefactorSuggestionModel(BaseModel):
    suggestion_id: str
    session_id: str
    file_path: str
    start_line: int
    end_line: int
    original_code: str
    proposed_code: str
    rationale: str
    confidence_score: float


class ComplianceMetricModel(BaseModel):
    metric_id: str
    session_id: str
    policy_score: float
    complexity_delta: float
    test_pass_rate: float
    latency_ms: int
    token_usage: int


class RefactorSessionModel(BaseModel):
    session_id: str
    user_id: str
    repo: Optional[str] = None
    branch: Optional[str] = None
    language: str
    policy_profile_id: str
    created_at: datetime
    status: str
    suggestions: List[RefactorSuggestionModel] = Field(default_factory=list)
    metrics: Optional[ComplianceMetricModel] = None


class PolicyImportRequest(BaseModel):
    document: str
    name: Optional[str] = None
    domain: Optional[str] = None
    version: Optional[str] = None


class RefactorRequest(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None
    code: str
    language: str
    policy_profile_id: str
    repo: Optional[str] = None
    branch: Optional[str] = None
    file_path: Optional[str] = None


class RefactorResponse(BaseModel):
    session: RefactorSessionModel
    suggestions: List[RefactorSuggestionModel]
    compliance: ComplianceMetricModel
    violations: List[dict]
    original_code: str
    refactored_code: str


