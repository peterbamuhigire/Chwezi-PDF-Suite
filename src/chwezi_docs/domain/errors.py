"""Stable, user-actionable exception hierarchy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(eq=False)
class ChweziError(Exception):
    """Base error safe to translate at CLI, desktop, SDK, or HTTP boundaries."""

    code: str = "CHWEZI_ERROR"
    message: str = "The document operation could not be completed."
    detail: str = ""
    suggested_action: str = "Review the operation inputs and diagnostic log."
    retryable: bool = False

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
            "suggested_action": self.suggested_action,
            "retryable": self.retryable,
        }


class UnsupportedFormatError(ChweziError):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            code="UNSUPPORTED_FORMAT",
            message="The input format is not supported.",
            **kwargs,  # type: ignore[arg-type]
        )


class UnsupportedConversionError(ChweziError):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            code="UNSUPPORTED_CONVERSION",
            message="No supported conversion path was found.",
            **kwargs,  # type: ignore[arg-type]
        )


class MissingCapabilityError(ChweziError):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            code="MISSING_CAPABILITY",
            message="This conversion requires an optional capability that is not available.",
            **kwargs,  # type: ignore[arg-type]
        )


class InvalidDocumentError(ChweziError):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            code="INVALID_DOCUMENT",
            message="The input document could not be validated.",
            **kwargs,  # type: ignore[arg-type]
        )


class OutputCollisionError(ChweziError):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            code="OUTPUT_COLLISION",
            message="The requested output already exists.",
            **kwargs,  # type: ignore[arg-type]
        )


class ConversionFailedError(ChweziError):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            code="CONVERSION_FAILED",
            message="The converter did not produce a valid output.",
            **kwargs,  # type: ignore[arg-type]
        )
