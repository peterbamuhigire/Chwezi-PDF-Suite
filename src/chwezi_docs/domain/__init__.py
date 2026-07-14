"""Public domain contracts for Chwezi Document Suite."""

from .errors import (
    ChweziError,
    ConversionFailedError,
    InvalidDocumentError,
    MissingCapabilityError,
    OutputCollisionError,
    UnsupportedConversionError,
    UnsupportedFormatError,
)
from .formats import DocumentFormat, FidelityClass, OverwritePolicy
from .jobs import JobStatus
from .results import ConversionRequest, ConversionResult, ConversionWarning

__all__ = [
    "ChweziError",
    "ConversionFailedError",
    "ConversionRequest",
    "ConversionResult",
    "ConversionWarning",
    "DocumentFormat",
    "FidelityClass",
    "InvalidDocumentError",
    "JobStatus",
    "MissingCapabilityError",
    "OutputCollisionError",
    "OverwritePolicy",
    "UnsupportedConversionError",
    "UnsupportedFormatError",
]
