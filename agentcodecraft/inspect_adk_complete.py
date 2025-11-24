"""Comprehensive ADK API inspection to find correct usage patterns."""
import inspect

print("=" * 70)
print("COMPREHENSIVE ADK API INSPECTION")
print("=" * 70)

# ============================================================================
# 1. Check main google.adk module
# ============================================================================
print("\n" + "=" * 70)
print("1. MAIN MODULE: google.adk")
print("=" * 70)

try:
    import google.adk
    print(f"✅ google.adk imported")
    print(f"   Location: {google.adk.__file__}")
    
    print("\n📦 All exports from google.adk:")
    exports = [name for name in dir(google.adk) if not name.startswith('_')]
    for export in sorted(exports):
        obj = getattr(google.adk, export)
        obj_type = type(obj).__name__
        if inspect.ismodule(obj):
            print(f"   📁 {export:25s} (module)")
        elif inspect.isclass(obj):
            print(f"   📦 {export:25s} (class)")
        elif callable(obj):
            print(f"   ⚙️  {export:25s} (function/callable)")
        else:
            print(f"   📄 {export:25s} ({obj_type})")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# 2. Check google.adk.tools module
# ============================================================================
print("\n" + "=" * 70)
print("2. TOOLS MODULE: google.adk.tools")
print("=" * 70)

try:
    import google.adk.tools
    print(f"✅ google.adk.tools imported")
    
    print("\n📦 All exports from google.adk.tools:")
    tool_exports = [name for name in dir(google.adk.tools) if not name.startswith('_')]
    for export in sorted(tool_exports):
        obj = getattr(google.adk.tools, export)
        obj_type = type(obj).__name__
        if inspect.ismodule(obj):
            print(f"   📁 {export:25s} (module)")
        elif inspect.isclass(obj):
            print(f"   📦 {export:25s} (class)")
        elif callable(obj):
            print(f"   ⚙️  {export:25s} (function/callable)")
        else:
            print(f"   📄 {export:25s} ({obj_type})")
    
    # Inspect FunctionTool in detail
    if 'FunctionTool' in tool_exports:
        print("\n🔍 DETAILED: FunctionTool class")
        print("-" * 70)
        from google.adk.tools import FunctionTool
        
        print(f"   Type: {type(FunctionTool)}")
        print(f"   Is class: {inspect.isclass(FunctionTool)}")
        
        print("\n   📋 All attributes/methods:")
        func_tool_attrs = [m for m in dir(FunctionTool) if not m.startswith('_')]
        for attr in sorted(func_tool_attrs):
            obj = getattr(FunctionTool, attr)
            if inspect.ismethod(obj) or inspect.isfunction(obj) or inspect.isbuiltin(obj):
                try:
                    sig = inspect.signature(obj)
                    print(f"      ⚙️  {attr:25s} {sig}")
                except:
                    print(f"      ⚙️  {attr:25s} (callable, cannot inspect)")
            elif inspect.isclass(obj):
                print(f"      📦 {attr:25s} (class)")
            else:
                print(f"      📄 {attr:25s} ({type(obj).__name__})")
        
        # Try to create a tool and inspect the instance
        print("\n   🧪 Creating FunctionTool instance:")
        def test_func(x: str) -> str:
            """Test function."""
            return f"Hello {x}"
        
        try:
            tool_instance = FunctionTool(test_func)
            print(f"      ✅ Created: {tool_instance}")
            print(f"      Type: {type(tool_instance)}")
            
            print("\n      📋 Instance methods/attributes:")
            instance_attrs = [m for m in dir(tool_instance) if not m.startswith('_')]
            for attr in sorted(instance_attrs):
                obj = getattr(tool_instance, attr)
                if inspect.ismethod(obj) or inspect.isfunction(obj):
                    try:
                        sig = inspect.signature(obj)
                        print(f"         ⚙️  {attr:25s} {sig}")
                    except:
                        print(f"         ⚙️  {attr:25s} (callable)")
                elif not callable(obj):
                    print(f"         📄 {attr:25s} = {obj}")
            
            # Try to call the tool
            print("\n      🧪 Testing tool execution:")
            if hasattr(tool_instance, 'execute'):
                try:
                    result = tool_instance.execute(x="World")
                    print(f"         ✅ tool.execute() works: {result}")
                except Exception as e:
                    print(f"         ❌ tool.execute() failed: {e}")
            elif hasattr(tool_instance, '__call__'):
                try:
                    result = tool_instance(x="World")
                    print(f"         ✅ tool() works: {result}")
                except Exception as e:
                    print(f"         ❌ tool() failed: {e}")
            elif callable(tool_instance):
                try:
                    result = tool_instance(x="World")
                    print(f"         ✅ tool is callable: {result}")
                except Exception as e:
                    print(f"         ❌ tool callable failed: {e}")
            else:
                print(f"         ⚠️  Tool doesn't seem directly callable")
                print(f"         Try: tool.run(), tool.invoke(), tool.call()")
                
        except Exception as e:
            print(f"      ❌ Failed to create FunctionTool: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 3. Check google.adk.agents module
# ============================================================================
print("\n" + "=" * 70)
print("3. AGENTS MODULE: google.adk.agents")
print("=" * 70)

try:
    import google.adk.agents
    print(f"✅ google.adk.agents imported")
    
    print("\n📦 All exports from google.adk.agents:")
    agent_exports = [name for name in dir(google.adk.agents) if not name.startswith('_')]
    for export in sorted(agent_exports):
        obj = getattr(google.adk.agents, export)
        obj_type = type(obj).__name__
        if inspect.ismodule(obj):
            print(f"   📁 {export:25s} (module)")
        elif inspect.isclass(obj):
            print(f"   📦 {export:25s} (class)")
        elif callable(obj):
            print(f"   ⚙️  {export:25s} (function/callable)")
        else:
            print(f"   📄 {export:25s} ({obj_type})")
            
    # Inspect LlmAgent if available
    if 'LlmAgent' in agent_exports:
        print("\n🔍 DETAILED: LlmAgent class")
        print("-" * 70)
        from google.adk.agents import LlmAgent
        
        print(f"   Type: {type(LlmAgent)}")
        
        print("\n   📋 Key methods (first 20):")
        llm_agent_attrs = [m for m in dir(LlmAgent) if not m.startswith('_')][:20]
        for attr in sorted(llm_agent_attrs):
            obj = getattr(LlmAgent, attr)
            if inspect.ismethod(obj) or inspect.isfunction(obj):
                try:
                    sig = inspect.signature(obj)
                    print(f"      ⚙️  {attr:25s} {sig}")
                except:
                    print(f"      ⚙️  {attr:25s} (callable)")
                    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# 4. Check other important modules
# ============================================================================
print("\n" + "=" * 70)
print("4. OTHER MODULES")
print("=" * 70)

modules_to_check = ['models', 'apps', 'sessions', 'memory']
for mod_name in modules_to_check:
    try:
        mod = __import__(f'google.adk.{mod_name}', fromlist=[mod_name])
        print(f"\n✅ google.adk.{mod_name}")
        exports = [name for name in dir(mod) if not name.startswith('_')]
        print(f"   Exports: {', '.join(exports[:10])}")
        if len(exports) > 10:
            print(f"   ... and {len(exports) - 10} more")
    except ImportError:
        print(f"\n❌ google.adk.{mod_name} not found")
    except Exception as e:
        print(f"\n⚠️  google.adk.{mod_name} error: {e}")

# ============================================================================
# 5. Summary and recommendations
# ============================================================================
print("\n" + "=" * 70)
print("5. SUMMARY & RECOMMENDATIONS")
print("=" * 70)

print("\n📝 Based on inspection, use:")
print("   1. Check FunctionTool instance methods above")
print("   2. Check how to call/execute tools")
print("   3. Update code to use correct API")

print("\n" + "=" * 70)
print("Inspection complete!")
print("=" * 70)

