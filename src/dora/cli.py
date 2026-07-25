"""CLI para calcular metricas DORA a partir de um arquivo JSON de eventos."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from .metrics import build_report
from .models import Deployment, Incident
from .report import to_text


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_events(path: str) -> tuple[list[Deployment], list[Incident]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    deployments = [
        Deployment(
            id=item["id"],
            committed_at=_parse_dt(item["committed_at"]),
            deployed_at=_parse_dt(item["deployed_at"]),
            caused_incident=item.get("caused_incident", False),
        )
        for item in data.get("deployments", [])
    ]
    incidents = [
        Incident(
            id=item["id"],
            deployment_id=item["deployment_id"],
            opened_at=_parse_dt(item["opened_at"]),
            resolved_at=_parse_dt(item["resolved_at"]),
        )
        for item in data.get("incidents", [])
    ]
    return deployments, incidents


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calculadora de metricas DORA")
    parser.add_argument("events_file", help="Caminho para o JSON de deploys/incidentes")
    parser.add_argument("--period-days", type=int, default=30, help="Janela de analise em dias")
    args = parser.parse_args(argv)

    deployments, incidents = load_events(args.events_file)
    report = build_report(deployments, incidents, args.period_days)
    print(to_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
