"""Testes do pacote de metricas DORA."""
from __future__ import annotations

from datetime import datetime

import pytest

from dora.metrics import (
    build_report,
    change_failure_rate,
    classify_change_failure_rate,
    classify_deployment_frequency,
    classify_lead_time,
    classify_mttr,
    deployment_frequency,
    lead_time_median_hours,
    mttr_median_hours,
)
from dora.models import Deployment, Incident
from dora.report import overall_level, to_text


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def test_deployment_frequency_basic():
    deployments = [
        Deployment("d1", _dt("2026-07-01T09:00"), _dt("2026-07-01T10:00")),
        Deployment("d2", _dt("2026-07-02T09:00"), _dt("2026-07-02T10:00")),
    ]
    assert deployment_frequency(deployments, period_days=10) == pytest.approx(0.2)


def test_deployment_frequency_requires_positive_period():
    with pytest.raises(ValueError):
        deployment_frequency([], period_days=0)


def test_lead_time_median_hours():
    deployments = [
        Deployment("d1", _dt("2026-07-01T00:00"), _dt("2026-07-01T02:00")),
        Deployment("d2", _dt("2026-07-01T00:00"), _dt("2026-07-01T06:00")),
        Deployment("d3", _dt("2026-07-01T00:00"), _dt("2026-07-01T10:00")),
    ]
    assert lead_time_median_hours(deployments) == pytest.approx(6.0)


def test_lead_time_empty_is_zero():
    assert lead_time_median_hours([]) == 0.0


def test_deployment_rejects_negative_lead_time():
    d = Deployment("d1", _dt("2026-07-02T00:00"), _dt("2026-07-01T00:00"))
    with pytest.raises(ValueError):
        d.lead_time_hours()


def test_change_failure_rate():
    deployments = [
        Deployment("d1", _dt("2026-07-01T00:00"), _dt("2026-07-01T01:00"), caused_incident=True),
        Deployment("d2", _dt("2026-07-01T00:00"), _dt("2026-07-01T01:00"), caused_incident=False),
        Deployment("d3", _dt("2026-07-01T00:00"), _dt("2026-07-01T01:00"), caused_incident=False),
        Deployment("d4", _dt("2026-07-01T00:00"), _dt("2026-07-01T01:00"), caused_incident=False),
    ]
    assert change_failure_rate(deployments) == pytest.approx(25.0)


def test_mttr_median_hours():
    incidents = [
        Incident("i1", "d1", _dt("2026-07-01T00:00"), _dt("2026-07-01T01:00")),
        Incident("i2", "d2", _dt("2026-07-01T00:00"), _dt("2026-07-01T05:00")),
    ]
    assert mttr_median_hours(incidents) == pytest.approx(3.0)


@pytest.mark.parametrize(
    "per_day,expected",
    [(2.0, "Elite"), (1.0, "Elite"), (0.5, "High"), (1 / 30, "Medium"), (1 / 365, "Low")],
)
def test_classify_deployment_frequency(per_day, expected):
    assert classify_deployment_frequency(per_day) == expected


@pytest.mark.parametrize(
    "hours,expected",
    [(2, "Elite"), (24, "Elite"), (72, "High"), (24 * 30, "Medium"), (24 * 365, "Low")],
)
def test_classify_lead_time(hours, expected):
    assert classify_lead_time(hours) == expected


@pytest.mark.parametrize(
    "pct,expected",
    [(0, "Elite"), (15, "Elite"), (25, "High"), (40, "Medium"), (60, "Low")],
)
def test_classify_change_failure_rate(pct, expected):
    assert classify_change_failure_rate(pct) == expected


@pytest.mark.parametrize(
    "hours,expected",
    [(0.5, "Elite"), (10, "High"), (100, "Medium"), (500, "Low")],
)
def test_classify_mttr(hours, expected):
    assert classify_mttr(hours) == expected


def test_build_report_and_overall_level_end_to_end():
    deployments = [
        Deployment("d1", _dt("2026-07-01T09:00"), _dt("2026-07-01T10:00"), caused_incident=False),
        Deployment("d2", _dt("2026-07-05T09:00"), _dt("2026-07-05T10:00"), caused_incident=True),
    ]
    incidents = [Incident("i1", "d2", _dt("2026-07-05T10:10"), _dt("2026-07-05T11:10"))]

    report = build_report(deployments, incidents, period_days=15)

    assert report.deployment_frequency_per_day == pytest.approx(2 / 15)
    assert report.change_failure_rate_pct == pytest.approx(50.0)
    assert overall_level(report) in {"Elite", "High", "Medium", "Low"}
    text = to_text(report)
    assert "Deployment Frequency" in text
    assert "Classificacao geral" in text
