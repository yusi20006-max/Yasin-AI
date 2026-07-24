"""Unit and integration tests for YasinAI Deployment System."""

import os
import shutil
import pytest
from unittest.mock import patch

from yasinai.deployment.installer import Installer
from yasinai.deployment.docker_manager import DockerManager
from yasinai.deployment.package_builder import DeploymentPackageBuilder
from yasinai.deployment.health_check import HealthCheck
from yasinai.cli.main import main


# Clean up helper
@pytest.fixture
def temp_dirs():
    dirs = ["tests/temp_install", "tests/temp_release_dist"]
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
    yield dirs
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)


def test_installer(temp_dirs):
    target = "tests/temp_install"
    installer = Installer(target_dir=target)

    # 1. Environment validation
    env_report = installer.validate_environment()
    assert env_report["ready"] is True
    assert "python_version" in env_report

    # 2. Config generation
    success = installer.initialize_configuration()
    assert success is True
    assert os.path.exists(os.path.join(target, "config.json"))

    # Test re-running doesn't fail
    assert installer.initialize_configuration() is True

    # 3. Overall Install process
    installer2 = Installer(target_dir=target)
    install_res = installer2.install()
    assert install_res["success"] is True


def test_docker_manager():
    # Detect inside container or host (safe run either way)
    res = DockerManager.is_in_docker()
    assert isinstance(res, bool)

    # Validate generated config
    config = DockerManager.generate_container_config(port=9090, env_vars={"DEBUG": "true"})
    assert config["image"] == "yasinai:latest"
    assert config["ports"] == {"9090/tcp": 9090}
    assert config["environment"]["DEBUG"] == "true"
    assert config["environment"]["YASINAI_DOCKER"] == "true"


def test_package_builder(temp_dirs):
    project_root = "tests/temp_install"
    shutil.copytree("yasinai", os.path.join(project_root, "yasinai"))

    # Create fake setup.py inside temp project root
    with open(os.path.join(project_root, "setup.py"), "w") as f:
        f.write("# Dummy setup")

    # Validate structure
    errors = DeploymentPackageBuilder.validate_project_structure(project_root)
    assert len(errors) == 0

    # Build release archive
    dist_dir = "tests/temp_release_dist"
    archive = DeploymentPackageBuilder.build_release_artifact(project_root, output_path=dist_dir)
    assert archive is not None
    assert os.path.exists(archive)
    assert archive.endswith(".zip")


def test_health_check():
    report = HealthCheck.run_all()
    assert report["status"] in ("HEALTHY", "DEGRADED", "UNHEALTHY")
    assert "platforms" in report
    assert report["platforms"]["core_runtime"]["available"] is True


def test_cli_integration():
    with patch("sys.stdout") as mock_stdout:
        # 1. Test 'yasin health check'
        exit_code = main(["health", "check"])
        assert exit_code == 0

        printed_calls = [call[0][0] for call in mock_stdout.write.call_args_list if call[0]]
        full_output = "".join(printed_calls)
        assert "Running system deployment readiness check..." in full_output
        assert "Deployment Readiness Report:" in full_output

        # 2. Test 'yasin package build'
        exit_code_build = main(["package", "build", "/tmp/project"])
        assert exit_code_build == 0
