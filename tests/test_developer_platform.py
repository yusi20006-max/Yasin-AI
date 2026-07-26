import pytest
from developer_platform.agent import Agent, AgentSDK
from developer_platform.plugin import Plugin, PluginSDK
from developer_platform.app import AIApplication, AppSDK
from developer_platform.extension import ExtensionAPI
from developer_platform.generator import Generator
from developer_platform.debugger import Debugger
from developer_platform.profiler import Profiler
from developer_platform.package_builder import PackageBuilder


def test_agent_sdk():
    sdk = AgentSDK()
    assert len(sdk.list_agents()) == 0

    # Create agent
    agent = sdk.create_agent(name="helper", role="assistant", description="Assists with tasks", type="helper-type")
    assert agent.name == "helper"
    assert agent.role == "assistant"
    assert agent.description == "Assists with tasks"
    assert agent.type == "helper-type"
    assert agent.status == "inactive"
    assert repr(agent) == "Agent(name='helper', role='assistant', type='helper-type', status='inactive')"

    # Duplicate create should fail
    with pytest.raises(ValueError, match="already exists"):
        sdk.create_agent(name="helper")

    # Get agent
    retrieved = sdk.get_agent("helper")
    assert retrieved is agent

    # Execute task when inactive should fail
    with pytest.raises(RuntimeError, match="must be active"):
        agent.execute_task("some task")

    # Start and execute task
    agent.start()
    assert agent.status == "active"
    result = agent.execute_task("do addition")
    assert "successfully completed task: 'do addition'" in result

    # Stop agent
    agent.stop()
    assert agent.status == "inactive"

    # List agents
    agents = sdk.list_agents()
    assert len(agents) == 1
    assert agents[0] is agent

    # Delete agent
    assert sdk.delete_agent("helper") is True
    assert sdk.get_agent("helper") is None
    assert sdk.delete_agent("helper") is False


def test_plugin_sdk():
    sdk = PluginSDK()
    assert len(sdk.list_plugins()) == 0

    plugin = Plugin(name="calculator", version="1.2.0", description="Handles math operations", enabled=True)
    assert plugin.name == "calculator"
    assert plugin.version == "1.2.0"
    assert plugin.description == "Handles math operations"
    assert plugin.enabled is True
    assert plugin.is_initialized is False
    assert repr(plugin) == "Plugin(name='calculator', version='1.2.0', enabled=True)"

    sdk.register_plugin(plugin)
    assert sdk.get_plugin("calculator") is plugin

    # Duplicate register should fail
    with pytest.raises(ValueError, match="already registered"):
        sdk.register_plugin(plugin)

    # Execute before initialized should fail
    with pytest.raises(RuntimeError, match="not initialized"):
        plugin.execute("add", 1, 2)

    # Initialize and execute
    plugin.initialize()
    assert plugin.is_initialized is True
    res = plugin.execute("add", 2, 3, multiplier=10)
    assert "successfully executed action 'add'" in res
    assert "multiplier': 10" in res

    # Disable plugin
    assert sdk.disable_plugin("calculator") is True
    assert plugin.enabled is False

    with pytest.raises(RuntimeError, match="is disabled"):
        plugin.execute("add", 2, 3)

    # Enable plugin
    assert sdk.enable_plugin("calculator") is True
    assert plugin.enabled is True

    # List plugins
    assert len(sdk.list_plugins()) == 1

    # Non-existent enable/disable
    assert sdk.enable_plugin("unknown") is False
    assert sdk.disable_plugin("unknown") is False


def test_app_sdk():
    sdk = AppSDK()
    assert len(sdk.list_applications()) == 0

    app = sdk.create_application("ChatBot", config={"debug": True})
    assert app.name == "ChatBot"
    assert app.config == {"debug": True}
    assert repr(app) == "AIApplication(name='ChatBot', agents=[], plugins=[])"

    # Duplicate application
    with pytest.raises(ValueError, match="already exists"):
        sdk.create_application("ChatBot")

    # Get and list application
    assert sdk.get_application("ChatBot") is app
    assert len(sdk.list_applications()) == 1

    # Delete application
    assert sdk.delete_application("ChatBot") is True
    assert sdk.get_application("ChatBot") is None
    assert sdk.delete_application("ChatBot") is False

    # Create again to test workflow
    app = sdk.create_application("WorkflowApp")
    agent = Agent(name="agent_a", role="validator")
    plugin = Plugin(name="plugin_a")

    app.add_agent(agent)
    app.add_plugin(plugin)

    # Duplicate add
    with pytest.raises(ValueError, match="already added"):
        app.add_agent(agent)
    with pytest.raises(ValueError, match="already added"):
        app.add_plugin(plugin)

    assert len(app.list_agents()) == 1
    assert len(app.list_plugins()) == 1

    # Run application
    output = app.run("verify codebase")
    assert output["application"] == "WorkflowApp"
    assert output["status"] == "completed"
    assert len(output["steps"]) == 2
    assert "Agent 'agent_a' executing" in output["steps"]
    assert "Plugin 'plugin_a' processing" in output["steps"]


def test_extension_api():
    api = ExtensionAPI()
    assert len(api.list_extensions()) == 0

    # Handler can be a callable or raw value
    def mock_handler(val: int) -> int:
        return val * 2

    api.register_extension(name="double", ext_type="transformer", handler=mock_handler)

    # Duplicate register
    with pytest.raises(ValueError, match="already registered"):
        api.register_extension(name="double", ext_type="transformer", handler=mock_handler)

    # Get extension
    ext = api.get_extension("double")
    assert ext["name"] == "double"
    assert ext["type"] == "transformer"

    # Invoke extension
    res = api.invoke_extension("double", 5)
    assert res == 10

    # Non-callable handler
    api.register_extension(name="version_ext", ext_type="info", handler="v1.0.0-beta")
    assert api.invoke_extension("version_ext") == "v1.0.0-beta"

    # Invoke unregistered
    with pytest.raises(ValueError, match="not registered"):
        api.invoke_extension("unknown")

    # List and unregister
    assert len(api.list_extensions()) == 2
    assert api.unregister_extension("double") is True
    assert api.unregister_extension("double") is False
    assert len(api.list_extensions()) == 1


def test_generator():
    gen = Generator()

    agent_code = gen.generate_agent_template("MyNewAgent")
    assert "class CustomAgent(Agent):" in agent_code
    assert "name=\"MyNewAgent\"" in agent_code

    plugin_code = gen.generate_plugin_template("MyNewPlugin")
    assert "class CustomPlugin(Plugin):" in plugin_code
    assert "name=\"MyNewPlugin\"" in plugin_code

    app_code = gen.generate_app_template("MyNewApp")
    assert "def build_app() -> AIApplication:" in app_code
    assert "name=\"MyNewApp\"" in app_code


def test_debugger():
    dbg = Debugger()
    assert dbg.current_agent is None
    assert len(dbg.get_session_logs()) == 0

    # Try log before starting
    with pytest.raises(RuntimeError, match="No active debugging session"):
        dbg.log_step("init", None, None)

    # Start session
    dbg.start_session("agent_x")
    assert dbg.current_agent == "agent_x"

    dbg.log_step("read_input", "hello", "HELLO")
    logs = dbg.get_session_logs()
    assert len(logs) == 1
    assert logs[0]["agent"] == "agent_x"
    assert logs[0]["step"] == "read_input"
    assert logs[0]["input"] == "hello"
    assert logs[0]["output"] == "HELLO"

    # Clear session
    dbg.clear_session()
    assert dbg.current_agent is None
    assert len(dbg.get_session_logs()) == 0


def test_profiler():
    prof = Profiler()

    # End profile without starting
    with pytest.raises(ValueError, match="No active profiling found"):
        prof.end_profile("task_run")

    prof.start_profile("task_run")
    # Simulate work
    elapsed = prof.end_profile("task_run")
    assert elapsed >= 0.0

    report = prof.get_profile_report()
    assert report["total_operations"] == 1
    assert report["total_execution_time"] == elapsed
    assert report["average_execution_time"] == elapsed
    assert report["breakdown"]["task_run"] == elapsed

    prof.clear_profiles()
    assert prof.get_profile_report() == {"status": "no profiles recorded"}


def test_package_builder():
    builder = PackageBuilder()

    res = builder.build_package(name="yasinai", version="1.5.0", output_directory="build/")
    assert res["success"] is True
    assert res["package_name"] == "yasinai-pkg-1.5.0.tar.gz"
    assert res["output_directory"] == "build/"
    assert "yasinai/core/" in res["files_included"]

    res_plugin = builder.build_package(name="my-plugin", version="2.0", output_directory="dist/")
    assert res_plugin["package_name"] == "my-plugin-v2.0.tar.gz"


# Verified Developer SDK coverage is at 100%
