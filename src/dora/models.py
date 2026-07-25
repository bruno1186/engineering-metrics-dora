"""Dominio de dados para calculo de metricas DORA."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Deployment:
    """Um deploy em producao."""

    id: str
    committed_at: datetime
    deployed_at: datetime
    caused_incident: bool = False

    def lead_time_hours(self) -> float:
        delta = self.deployed_at - self.committed_at
        if delta.total_seconds() < 0:
            raise ValueError(f"deployed_at anterior a committed_at no deploy {self.id}")
        return delta.total_seconds() / 3600


@dataclass(frozen=True)
class Incident:
    """Um incidente causado por um deploy, com tempo de resolucao."""

    id: str
    deployment_id: str
    opened_at: datetime
    resolved_at: datetime

    def resolution_hours(self) -> float:
        delta = self.resolved_at - self.opened_at
        if delta.total_seconds() < 0:
            raise ValueError(f"resolved_at anterior a opened_at no incidente {self.id}")
        return delta.total_seconds() / 3600
