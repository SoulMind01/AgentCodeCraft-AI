"""Inspect actual ADK API to find correct tool creation method."""
import inspect

print("=" * 60)
print("Inspecting Google ADK API")
print("=" * 60)

try:
    from google.adk.tools import FunctionTool
    print("\n✅ FunctionTool imported successfully")
    print(f"   Type: {type(FunctionTool)}")
    
    print("\n📋 FunctionTool attributes:")
    attrs = [m for m in dir(FunctionTool) if not m.startswith('_')]
    for attr in attrs:
        obj = getattr(FunctionTool, attr)
        if inspect.ismethod(obj) or inspect.isfunction(obj):
            try:
                sig = inspect.signature(obj)
                print(f"   - {attr}{sig}")
            except:
                print(f"   - {attr} (callable)")
        else:
            print(f"   - {attr} ({type(obj).__name__})")
    
    print("\n🔍 Checking for tool creation methods:")
    
    # Check if from_callable exists
    if hasattr(FunctionTool, 'from_callable'):
        print("   ✅ FunctionTool.from_callable exists")
        print(f"      Signature: {inspect.signature(FunctionTool.from_callable)}")
    else:
        print("   ❌ FunctionTool.from_callable does NOT exist")
    
    # Check __init__
    if hasattr(FunctionTool, '__init__'):
        try:
            sig = inspect.signature(FunctionTool.__init__)
            print(f"   ✅ FunctionTool.__init__ exists")
            print(f"      Signature: {sig}")
        except:
            print("   ✅ FunctionTool.__init__ exists (cannot inspect signature)")
    
    # Try to find alternative methods
    print("\n🔍 Looking for alternative tool creation methods:")
    for attr in attrs:
        if 'callable' in attr.lower() or 'function' in attr.lower() or 'create' in attr.lower():
            obj = getattr(FunctionTool, attr)
            if callable(obj):
                try:
                    sig = inspect.signature(obj)
                    print(f"   Found: {attr}{sig}")
                except:
                    print(f"   Found: {attr} (callable)")
    
    # Check what's in the tools module
    print("\n📦 Checking google.adk.tools module:")
    import google.adk.tools
    tool_module_attrs = [x for x in dir(google.adk.tools) if not x.startswith('_')]
    print(f"   Available: {', '.join(tool_module_attrs)}")
    
    # Try to create a tool to see what works
    print("\n🧪 Testing tool creation:")
    def test_func(x: str) -> str:
        return f"Hello {x}"
    
    # Try different methods
    print("   Trying FunctionTool(test_func)...")
    try:
        tool1 = FunctionTool(test_func)
        print(f"      ✅ FunctionTool(func) works: {tool1}")
    except Exception as e:
        print(f"      ❌ FunctionTool(func) failed: {e}")
    
    print("   Trying FunctionTool.from_callable(test_func)...")
    try:
        tool2 = FunctionTool.from_callable(test_func)
        print(f"      ✅ FunctionTool.from_callable(func) works: {tool2}")
    except Exception as e:
        print(f"      ❌ FunctionTool.from_callable(func) failed: {e}")
    
    # Check if there's a factory function
    if hasattr(google.adk.tools, 'function_tool'):
        print("   Trying function_tool(test_func)...")
        try:
            tool3 = google.adk.tools.function_tool(test_func)
            print(f"      ✅ function_tool(func) works: {tool3}")
        except Exception as e:
            print(f"      ❌ function_tool(func) failed: {e}")
    
except ImportError as e:
    print(f"\n❌ Could not import: {e}")
    print("   Make sure you're in the virtual environment!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

