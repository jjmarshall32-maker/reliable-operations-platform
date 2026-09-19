from reliable_ops.demo import run_demo


def test_demo_is_runnable_and_self_contained(tmp_path):
    result = run_demo(tmp_path)

    assert result["run_status"] == "success"
    assert result["coverage"] == {
        "source-a": "loaded",
        "source-b": "empty",
        "source-c": "malformed",
    }
    assert result["freshness"] == "fresh"
    assert result["integrity_ok"] is True
