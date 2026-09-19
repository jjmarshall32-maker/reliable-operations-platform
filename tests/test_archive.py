from reliable_ops.archive import archive_bytes


def test_archive_is_content_addressed_and_idempotent(tmp_path):
    first = archive_bytes(tmp_path, "source-a", b"hello")
    second = archive_bytes(tmp_path, "source-a", b"hello")
    third = archive_bytes(tmp_path, "source-a", b"different")

    assert first == second
    assert first.read_bytes() == b"hello"
    assert third != first
