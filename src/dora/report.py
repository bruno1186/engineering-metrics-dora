"""Geracao de relatorio textual a partir de um DoraReport."""
from __future__ import annotations

from .metrics import DoraReport

_LEVEL_ORDER = {"Elite": 0, "High": 1, "Medium": 2, "Low": 3}


def overall_level(report: DoraReport) -> str:
    levels = [
        report.deployment_frequency_level,
        report.lead_time_level,
        report.change_failure_rate_level,
        report.mttr_level,
    ]
    worst = max(levels, key=lambda lvl: _LEVEL_ORDER[lvl])
    return worst


def to_text(report: DoraReport) -> str:
    lines = [
        f"Periodo analisado: {report.period_days} dias",
        f"Deployment Frequency: {report.deployment_frequency_per_day:.2f}/dia -> {report.deployment_frequency_level}",
        f"Lead Time for Changes (mediana): {report.lead_time_median_hours:.1f}h -> {report.lead_time_level}",
        f"Change Failure Rate: {report.change_failure_rate_pct:.1f}% -> {report.change_failure_rate_level}",
        f"MTTR (mediana): {report.mttr_median_hours:.1f}h -> {report.mttr_level}",
        f"Classificacao geral (pior indicador): {overall_level(report)}",
    ]
    return "\n".join(lines)
