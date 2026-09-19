from reliable_ops.coverage import ExpectedSource, classify_coverage
from reliable_ops.models import CoverageStatus


def test_expected_but_unobserved_source_is_missing():
    result = classify_coverage(
        [ExpectedSource("a"), ExpectedSource("b"), ExpectedSource("c")],
        {"a": CoverageStatus.LOADED, "b": CoverageStatus.EMPTY},
    )

    assert result == {
        "a": CoverageStatus.LOADED,
        "b": CoverageStatus.EMPTY,
        "c": CoverageStatus.MISSING,
    }


def test_newly_observed_source_remains_visible():
    result = classify_coverage(
        [ExpectedSource("a")],
        {"a": CoverageStatus.LOADED, "new-source": CoverageStatus.LOADED},
    )
    assert result["new-source"] == CoverageStatus.LOADED
