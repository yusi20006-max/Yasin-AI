import os
import json
import pytest
from unittest.mock import MagicMock, patch
from yasinai.deployment.installer import Installer
from yasinai.deployment.docker_manager import DockerManager
from yasinai.deployment.health_check import HealthCheck
from yasinai.deployment.package_builder import PackageBuilder


# 1. Tests for Installer
def test_installer_verify_environment(tmp_path):
    installer = Installer(target_directory=str(tmp_path))
    env_info = installer.verify_environment()
    assert env_info["python_ok"] is True
    assert env_info["write_ok"] is True
    assert env_info["success"] is True


def test_installer_setup_directories(tmp_path):
    installer = Installer(target_directory=str(tmp_path))
    created_dirs = installer.setup_directories()
    assert len(created_dirs) == 3
    for d in created_dirs:
        assert os.path.exists(d)

    # Calling it again shouldn't create them again or fail
    second_created = installer.setup_directories()
    assert len(second_created) == 0


def test_installer_install(tmp_path):
    installer = Installer(target_directory=str(tmp_path))
    result = installer.install()
    assert result["success"] is True
    assert result["config_created"] is True
    assert os.path.exists(os.path.join(tmp_path, "config", "config.json"))

    # Running installer again shouldn't recreate/overwrite existing config
    result_second = installer.install()
    assert result_second["success"] is True
    assert result_second["config_created"] is False


# 2. Tests for DockerManager
def test_docker_manager_availability_checks():
    manager = DockerManager()
    # Shutil/subprocess check mock
    with patch("shutil.which", return_value="/usr/bin/docker"):
        assert manager.check_docker_available() is True

    with patch("shutil.which", return_value=None):
        assert manager.check_docker_available() is False


def test_docker_manager_compose_checks():
    manager = DockerManager()
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/docker-compose" if name == "docker-compose" else None):
        assert manager.check_docker_compose_available() is True

    # Test "docker compose" subcommand check
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/docker" if name == "docker" else None):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert manager.check_docker_compose_available() is True


def test_docker_manager_generation(tmp_path):
    manager = DockerManager(root_directory=str(tmp_path))
    res = manager.generate_docker_files()
    assert res["dockerfile_created"] is True
    assert res["compose_created"] is True

    assert os.path.exists(os.path.join(tmp_path, "Dockerfile"))
    assert os.path.exists(os.path.join(tmp_path, "docker-compose.yml"))

    # Shouldn't recreate files if they exist and overwrite is False
    res_second = manager.generate_docker_files(overwrite=False)
    assert res_second["dockerfile_created"] is False
    assert res_second["compose_created"] is False


def test_docker_manager_status(tmp_path):
    manager = DockerManager(root_directory=str(tmp_path))
    status = manager.get_docker_status()
    assert status["dockerfile_exists"] is False
    assert status["docker_compose_exists"] is False

    manager.generate_docker_files()
    status_after = manager.get_docker_status()
    assert status_after["dockerfile_exists"] is True
    assert status_after["docker_compose_exists"] is True


# 3. Tests for HealthCheck
def test_health_check_runtime():
    health = HealthCheck()
    result = health.check_runtime()
    assert result["success"] is True
    assert "Core Runtime loaded" in result["message"]
    assert "version" in result["details"]


def test_health_check_cli():
    health = HealthCheck()
    result = health.check_cli()
    assert result["success"] is True
    assert "CLI parser instantiated successfully" in result["message"]
    assert "status" in result["subcommands_found"]


def test_health_check_security():
    health = HealthCheck()
    result = health.check_security_platform()
    assert result["success"] is True
    assert result["identity_ok"] is True
    assert result["encryption_ok"] is True


def test_health_check_knowledge():
    health = HealthCheck()
    result = health.check_knowledge_platform()
    assert result["success"] is True
    assert result["memory_ok"] is True
    assert result["search_ok"] is True


def test_health_check_run_all():
    health = HealthCheck()
    result = health.run_all_checks()
    assert result["success"] is True
    assert result["status"] == "HEALTHY"
    assert "runtime" in result["platforms"]


# 4. Tests for PackageBuilder
def test_package_builder_build():
    builder = PackageBuilder()
    res = builder.build_package(name="yasinai", version="1.0.0", output_directory="dist/")
    assert res["success"] is True
    assert res["package_name"] == "yasinai-pkg-1.0.0.tar.gz"
    assert "yasinai/core/" in res["files_included"]

    res_other = builder.build_package(name="custom-plugin", version="2.5", output_directory="temp/")
    assert res_other["package_name"] == "custom-plugin-v2.5.tar.gz"
