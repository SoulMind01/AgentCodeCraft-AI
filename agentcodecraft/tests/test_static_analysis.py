from app.services.static_analysis import StaticAnalysisService


def test_compute_complexity_increases_with_lines():
    service = StaticAnalysisService()
    simple = "print('hello')\n"
    complex_code = "def foo():\n    for i in range(10):\n        if i % 2 == 0:\n            print(i)\n"
    assert service.compute_complexity(complex_code) > service.compute_complexity(simple)


def test_summarize_complexity():
    service = StaticAnalysisService()
    original = "print('a')\n"
    refactored = "def foo():\n    print('a')\n"
    delta = service.summarize_complexity(original, refactored)
    assert delta > 0


