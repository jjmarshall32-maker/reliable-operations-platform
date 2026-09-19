from datetime import date

from reliable_ops.integrity import compare_layer_counts


def test_layer_counts_reconcile_when_dates_and_counts_match():
    counts = {date(2030, 1, 1): 10, date(2030, 1, 2): 12}
    assert compare_layer_counts(counts, counts).ok is True


def test_integrity_report_exposes_gaps_and_count_mismatches():
    result = compare_layer_counts(
        {date(2030, 1, 1): 10, date(2030, 1, 2): 12},
        {date(2030, 1, 1): 9, date(2030, 1, 3): 4},
    )

    assert result.ok is False
    assert result.missing_in_staging == (date(2030, 1, 2),)
    assert result.missing_in_raw == (date(2030, 1, 3),)
    assert result.row_count_mismatches[0].raw_rows == 10
    assert result.row_count_mismatches[0].staging_rows == 9
