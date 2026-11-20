from typing import Literal

from pydantic import BaseModel, ConfigDict


class Metric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float | None = None
    unit: str | None = None
    evidence: str | None = None


class Risk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    severity: Literal["low", "medium", "high"]
    evidence: str


class FinancialExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: str | None = None
    period: str | None = None
    revenue: Metric | None = None
    ebitda: Metric | None = None
    net_debt: Metric | None = None
    risks: list[Risk] = []