from chwezi_docs.domain.errors import OutputCollisionError


def test_domain_error_serialises_stable_fields() -> None:
    error = OutputCollisionError(
        detail="output/report.md exists",
        suggested_action="Choose rename.",
    )

    assert error.to_dict() == {
        "code": "OUTPUT_COLLISION",
        "message": "The requested output already exists.",
        "detail": "output/report.md exists",
        "suggested_action": "Choose rename.",
        "retryable": False,
    }
