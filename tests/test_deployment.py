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

    dockerfile = (tmp_path / "Dockerfile").read_text(encoding="utf-8")
    compose = (tmp_path / "docker-compose.yml").read_text(encoding="utf-8")
    assert "USER 10001:10001" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "no-new-privileges:true" in compose
    assert "cap_drop:" in compose
    assert "YASINAI_ENVIRONMENT" in compose
    assert "ENVIRONMENT=production" not in compose

    # Shouldn't recreate files if they exist and overwrite is False
    res_second = manager.generate_docker_files(overwrite=False)
    assert res_second["dockerfile_created"] is False
    assert res_second["compose_created"] is False

    # overwrite=True alone must not clobber existing files
    res_unsafe = manager.generate_docker_files(overwrite=True)
    assert res_unsafe["dockerfile_created"] is False
    assert res_unsafe["compose_created"] is False

    # Explicit dual confirmation required to replace existing files
    res_force = manager.generate_docker_files(
        overwrite=True, confirm_overwrite_production=True
    )
    assert res_force["dockerfile_created"] is True
    assert res_force["compose_created"] is True


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


def test_additional_deployment_coverage(tmp_path):
    # 1. DockerManager compose check subprocess exceptions (lines 47-51)
    manager = DockerManager()
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/docker" if name == "docker" else None):
        with patch("subprocess.run", side_effect=Exception("Subprocess failed")):
            assert manager.check_docker_compose_available() is False

    # DockerManager when check_docker_available is False (lines 50-51)
    with patch.object(DockerManager, "check_docker_available", return_value=False):
        assert manager.check_docker_compose_available() is False

    # DockerManager generate files IOError (lines 91-92, 101-102)
    # Mocking open to raise IOError when writing
    with patch("builtins.open", side_effect=IOError("Disk full")):
        res = manager.generate_docker_files(overwrite=True)
        assert res["dockerfile_created"] is False
        assert res["compose_created"] is False

    # 2. HealthCheck subplatform health checks exceptions (lines 58-60, 87-89, 122-124, 156-158)
    health = HealthCheck()
    with patch("yasinai.core.runtime.Runtime.start", side_effect=Exception("Runtime start error")):
        res = health.check_runtime()
        assert res["success"] is False
        assert "Runtime start error" in res["message"]

    with patch("yasinai.cli.main.create_parser", side_effect=Exception("Parser create error")):
        res = health.check_cli()
        assert res["success"] is False
        assert "Parser create error" in res["message"]

    with patch("security_platform.identity.IdentityManager", side_effect=Exception("Identity error")):
        res = health.check_security_platform()
        assert res["success"] is False
        assert "Identity error" in res["message"]

    with patch("knowledge_platform.memory.MemoryManager", side_effect=Exception("Memory error")):
        res = health.check_knowledge_platform()
        assert res["success"] is False
        assert "Memory error" in res["message"]

    # 3. Installer setup_directories exceptions (lines 64-65)
    installer = Installer(target_directory=str(tmp_path))
    with patch("os.makedirs", side_effect=Exception("Permission denied")):
        # directory setup logs the error and continues, returning empty list of newly created directories
        res = installer.setup_directories()
        assert len(res) == 0

    # Installer environment verification failures (lines 75-76)
    with patch.object(Installer, "verify_environment", return_value={"success": False}):
        res = installer.install()
        assert res["success"] is False
        assert "Environment verification failed" in res["message"]

    # Installer environment template creation IOError (lines 101-102)
    with patch("builtins.open", side_effect=IOError("Cannot open file")):
        res = installer.install()
        assert res["success"] is True  # installation is successful but configuration creation is logged and skipped
        assert res["config_created"] is False

    # 4. PackageBuilder build exception (lines 43-45)
    builder = PackageBuilder()
    # pass None as name to trigger TypeError inside name check
    res = builder.build_package(name=None)
    assert res["success"] is False
    assert res["package_name"] == ""
