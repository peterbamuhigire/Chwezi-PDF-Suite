"""Read-only probes for optional Python and system capabilities."""

from __future__ import annotations

import importlib.util
import shutil
from dataclasses import dataclass
from typing import Any

from chwezi_docs.conversion.registry import (
    ConverterSpec,
    Requirement,
    RequirementKind,
    default_registry,
)


@dataclass(frozen=True, slots=True)
class CapabilityReport:
    converter: ConverterSpec
    available: bool
    missing: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.converter.name,
            "source_format": self.converter.source_format.value,
            "target_format": self.converter.target_format.value,
            "available": self.available,
            "fidelity": self.converter.fidelity.value,
            "lossy": self.converter.lossy,
            "requirements": [requirement.name for requirement in self.converter.requirements],
            "missing": list(self.missing),
            "description": self.converter.description,
        }


class CapabilityService:
    def __init__(self, registry: tuple[ConverterSpec, ...] | None = None) -> None:
        self.registry = registry or default_registry()

    @staticmethod
    def _module_available(module_name: str) -> bool:
        try:
            return importlib.util.find_spec(module_name) is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def requirement_available(self, requirement: Requirement) -> bool:
        if requirement.kind is RequirementKind.PYTHON_MODULE:
            return all(self._module_available(value) for value in requirement.values)
        if requirement.kind is RequirementKind.EXECUTABLE:
            return all(shutil.which(value) is not None for value in requirement.values)
        return any(
            shutil.which(value) is not None or self._module_available(value)
            for value in requirement.values
        )

    def inspect(self, converter: ConverterSpec) -> CapabilityReport:
        missing = tuple(
            f"{requirement.name}: {requirement.install_hint}"
            for requirement in converter.requirements
            if not self.requirement_available(requirement)
        )
        return CapabilityReport(
            converter=converter,
            available=converter.implemented and not missing,
            missing=missing,
        )

    def reports(self) -> tuple[CapabilityReport, ...]:
        return tuple(self.inspect(converter) for converter in self.registry)
