"""Deterministic, cycle-safe conversion path planning."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from chwezi_docs.application.capability_service import CapabilityService
from chwezi_docs.domain.errors import MissingCapabilityError, UnsupportedConversionError
from chwezi_docs.domain.formats import DocumentFormat

from .registry import ConverterSpec, default_registry


@dataclass(frozen=True, slots=True)
class ConversionPlan:
    source_format: DocumentFormat
    target_format: DocumentFormat
    steps: tuple[ConverterSpec, ...]

    @property
    def backends(self) -> tuple[str, ...]:
        return tuple(step.name for step in self.steps)


class ConversionPlanner:
    def __init__(
        self,
        registry: tuple[ConverterSpec, ...] | None = None,
        capabilities: CapabilityService | None = None,
    ) -> None:
        self.registry = registry or default_registry()
        self.capabilities = capabilities or CapabilityService(self.registry)

    def plan(self, source: DocumentFormat, target: DocumentFormat) -> ConversionPlan:
        queue: deque[tuple[DocumentFormat, tuple[ConverterSpec, ...]]] = deque([(source, ())])
        visited = {source}
        missing_routes: list[str] = []

        while queue:
            current, steps = queue.popleft()
            candidates = sorted(
                (edge for edge in self.registry if edge.source_format is current),
                key=lambda edge: (edge.lossy, edge.cost, edge.name),
            )
            for edge in candidates:
                report = self.capabilities.inspect(edge)
                if not report.available:
                    missing_routes.extend(report.missing)
                    continue
                next_steps = (*steps, edge)
                if edge.target_format is target:
                    return ConversionPlan(source, target, next_steps)
                if edge.target_format not in visited:
                    visited.add(edge.target_format)
                    queue.append((edge.target_format, next_steps))

        declared = any(
            edge.source_format is source and edge.target_format is target for edge in self.registry
        )
        if declared and missing_routes:
            raise MissingCapabilityError(
                detail="; ".join(dict.fromkeys(missing_routes)),
                suggested_action=(
                    "Install the named optional feature and rerun `chwezi capabilities`."
                ),
            )
        raise UnsupportedConversionError(
            detail=f"No implemented route from {source.value} to {target.value}.",
            suggested_action="Inspect `chwezi capabilities` for currently implemented routes.",
        )
