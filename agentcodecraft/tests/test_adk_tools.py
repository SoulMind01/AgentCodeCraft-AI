"""Unit tests for ADK tools."""
try:
    import pytest
except ImportError:
    pytest = None  # Allow running without pytest

from app.services.adk_tools import (
    StaticAnalysisTool,
    GeminiRefactorTool,
    TestRunnerTool
)


def test_static_analysis_tool():
    """Test StaticAnalysisTool execution."""
    code = "def hello():\n    print('world')"
    # CORRECT API: Use .func() for direct testing (tools use run_async() when called by agents)
    result = StaticAnalysisTool.func(code=code)
    
    assert "complexity" in result
    assert "line_count" in result
    assert "function_count" in result
    assert result["function_count"] == 1
    assert "hello" in result["functions"]
    print(f"✅ StaticAnalysisTool works: {result}")


def test_gemini_refactor_tool_creation():
    """Test GeminiRefactorTool can be created."""
    # Just verify it exists and can be imported
    assert GeminiRefactorTool is not None
    print("✅ GeminiRefactorTool created successfully")
    
    # Note: Full test requires API key and violations - will test in Phase 3


def test_test_runner_tool():
    """Test TestRunnerTool execution."""
    # Test with simple code that has a test
    code = "def test_example():\n    assert True"
    # CORRECT API: Use .func() for direct testing
    result = TestRunnerTool.func(code=code, language="python")
    
    assert "test_pass_rate" in result
    assert 0.0 <= result["test_pass_rate"] <= 1.0
    print(f"✅ TestRunnerTool works: test_pass_rate={result['test_pass_rate']}")


def test_test_runner_tool_no_tests():
    """Test TestRunnerTool with code that has no tests."""
    code = "def hello():\n    print('world')"
    # CORRECT API: Use .func() for direct testing
    result = TestRunnerTool.func(code=code, language="python")
    
    assert "test_pass_rate" in result
    assert 0.0 <= result["test_pass_rate"] <= 1.0
    print(f"✅ TestRunnerTool handles no tests: test_pass_rate={result['test_pass_rate']}")


def test_test_runner_tool_non_python():
    """Test TestRunnerTool with non-Python language."""
    code = "console.log('hello');"
    # CORRECT API: Use .func() for direct testing
    result = TestRunnerTool.func(code=code, language="javascript")
    
    assert "test_pass_rate" in result
    assert result["test_pass_rate"] == 1.0
    assert "message" in result
    print(f"✅ TestRunnerTool handles non-Python: {result['message']}")


if __name__ == "__main__":
    # Run tests directly
    print("=" * 60)
    print("Testing ADK Tools")
    print("=" * 60)
    
    try:
        test_static_analysis_tool()
        test_gemini_refactor_tool_creation()
        test_test_runner_tool()
        test_test_runner_tool_no_tests()
        test_test_runner_tool_non_python()
        
        print("\n" + "=" * 60)
        print("✅ All ADK tools tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

