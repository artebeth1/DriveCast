from app.memory.narration_memory import already_narrated, record, filter_candidates

def test_record_adds_name():
    narrated = []
    result = record("Willis Tower", narrated)
    assert already_narrated("Willis Tower", result)

def test_idempotent_record():
    narrated = []
    result1 = record("Willis Tower", narrated)
    result2 = record("Willis Tower", result1)
    assert result1 == result2

class FakeLandmark:
    def __init__(self, name):
        self.name = name

def test_filter_removes_narrated():
    a = FakeLandmark("Willis Tower")
    b = FakeLandmark("Cloud Gate")
    narrated = ["Willis Tower"]
    result = filter_candidates([a, b], narrated)
    assert a not in result and b in result