"""Calculo das quatro metricas DORA a partir de deploys e incidentes."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .models import Deployment, Incident

PerformanceLevel = str  # "Elite" | "High" | "Medium" | "Low"


@dataclass(frozen=True)
class DoraReport:
    period_days: int
    deployment_frequency_per_day: float
    lead_time_median_hours: float
    change_failure_rate_pct: float
    mttr_median_hours: float
    deployment_frequency_level: PerformanceLevel
    lead_time_level: PerformanceLevel
    change_failure_rate_level: PerformanceLevel
    mttr_level: PerformanceLevel


def deployment_frequency(deployments: list[Deployment], period_days: int) -> float:
    if period_days <= 0:
        raise ValueError("period_days deve ser positivo")
    return len(deployments) / period_days


def lead_time_median_hours(deployments: list[Deployment]) -> float:
    if not deployments:
        return 0.0
    return median(d.lead_time_hours() for d in deployments)


def change_failure_rate(deployments: list[Deployment]) -> float:
    if not deployments:
        return 0.0
    failed = sum(1 for d in deployments if d.caused_incident)
    return (failed / len(deployments)) * 100


def mttr_median_hours(incidents: list[Incident]) -> float:
    if not incidents:
        return 0.0
    return median(i.resolution_hours() for i in incidents)


def classify_deployment_frequency(per_day: float) -> PerformanceLevel:
    if per_day >= 1:
        return "Elite"
    if per_day >= 1 / 7:
        return "High"
    if per_day >= 1 / 180:
        return "Medium"
    return "Low"


def classify_lead_time(hours: float) -> PerformanceLevel:
    if hours <= 24:
        return "Elite"
    if hours <= 24 * 7:
        return "High"
    if hours <= 24 * 30 * 6:
        return "Medium"
    return "Low"


def classify_change_failure_rate(pct: float) -> PerformanceLevel:
    if pct <= 15:
        return "Elite"
    if pct <= 30:
        return "High"
    if pct <= 45:
        return "Medium"
    return "Low"


def classify_mttr(hours: float) -> PerformanceLevel:
    if hours <= 1:
        return "Elite"
    if hours <= 24:
        return "High"
    if hours <= 24 * 7:
        return "Medium"
    return "Low"


def build_report(deployments: list[Deployment], incidents: list[Incident], period_days: int) -> DoraReport:
    freq = deployment_frequency(deployments, period_days)
    lead = lead_time_median_hours(deployments)
    cfr = change_failure_rate(deployments)
    mttr = mttr_median_hours(incidents)
    return DoraReport(
        period_days=period_days,
        deployment_frequency_per_day=freq,
        lead_time_median_hours=lead,
        change_failure_rate_pct=cfr,
        mttr_median_hours=mttr,
        deployment_frequency_level=classify_deployment_frequency(freq),
        lead_time_level=classify_lead_time(lead),
        change_failure_rate_level=classify_change_failure_rate(cfr),
        mttr_level=classify_mttr(mttr),
    )
