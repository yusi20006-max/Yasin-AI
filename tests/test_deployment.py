import os
import tarfile
from unittest.mock import MagicMock, patch

from yasinai.deployment.docker_manager import DockerManager
from yasinai.deployment.health_check import HealthCheck
from yasinai.deployment.installer import Installer
from yasinai.deployment.package_builder import PackageBuilder


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
    second_created = installer.setup_directories()
    assert len(second_created) == 0


def test_installer_install(tmp_path):
    installer = Installer(target_directory=str(tmp_path))
    result = installer.install()
    assert result["success"] is True
    assert result["config_created"] is True
    assert os.path.exists(os.path.join(tmp_path, "config", "config.json"))
    result_second = installer.install()
    assert result_second["success"] is True
    assert result_second["config_created"] is False


def test_docker_manager_availability_checks():
    manager = DockerManager()
    with patch("shutil.which", return_value="/usr/bin/docker"):
        assert manager.check_docker_available() is True
    with patch("shutil.which", return_value=None):
        assert manager.check_docker_available() is False


def test_docker_manager_compose_checks():
    manager = DockerManager()
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/docker-compose" if name == "docker-compose" else None):
        assert manager.check_docker_compose_available() is True
    with (
        patch("shutil.which", side_effect=lambda name: "/usr/bin/docker" if name == "docker" else None),
        patch("subprocess.run") as mock_run,
    ):
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
    res_second = manager.generate_docker_files(overwrite=False)
    assert res_second["dockerfile_created"] is False
    assert res_second["compose_created"] is False
    res_unsafe = manager.generate_docker_files(overwrite=True)
    assert res_unsafe["dockerfile_created"] is False
    assert res_unsafe["compose_created"] is False
    res_force = manager.generate_docker_files(overwrite=True, confirm_overwrite_production=True)
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


def test_package_builder_build(tmp_path):
    builder = PackageBuilder()
    dist_dir = str(tmp_path / "dist") + "/"
    temp_dir = str(tmp_path / "temp") + "/"
    res = builder.build_package(name="yasinai", version="1.0.0", output_directory=dist_dir)
    assert res["success"] is True
    assert res["package_name"] == "yasinai-pkg-1.0.0.tar.gz"
    assert "yasinai/core/" in res["files_included"]
    res_other = builder.build_package(name="custom-plugin", version="2.5", output_directory=temp_dir)
    assert res_other["package_name"] == "custom-plugin-v2.5.tar.gz"


def test_package_builder_archive_member_names_are_safe(tmp_path):
    builder = PackageBuilder()
    source = tmp_path / "src"
    source.mkdir()
    (source / "module.py").write_text("print('hello')\n")
    config = tmp_path / "config.toml"
    config.write_text("[tool]\nname = 'demo'\n")
    output = tmp_path / "out"
    res = builder.build_package(
        name="demo",
        version="0.1.0",
        output_directory=str(output),
        include_paths=[str(source), str(config), "../pyproject.toml"],
    )
    assert res["success"] is True
    with tarfile.open(res["archive_path"], "r:gz") as archive:
        members = archive.getnames()
    assert members
    assert all(not member.startswith("/") for member in members)
    assert all(".." not in member.split("/") for member in members)


def test_package_builder_single_file_input(tmp_path):
    builder = PackageBuilder()
    source = tmp_path / "single.txt"
    source.write_text("single file\n")
    result = builder.build_package(
        name="single",
        output_directory=str(tmp_path / "out"),
        include_paths=[str(source)],
    )
    assert result["success"] is True
    with tarfile.open(result["archive_path"], "r:gz") as archive:
        assert archive.getnames() == ["single.txt"]


def test_additional_deployment_coverage(tmp_path):
    manager = DockerManager()
    with (
        patch("shutil.which", side_effect=lambda name: "/usr/bin/docker" if name == "docker" else None),
        patch("subprocess.run", side_effect=Exception("Subprocess failed")),
    ):
        assert manager.check_docker_compose_available() is False
    with patch.object(DockerManager, "check_docker_available", return_value=False):
        assert manager.check_docker_compose_available() is False
    with patch("builtins.open", side_effect=OSError("Disk full")):
        res = manager.generate_docker_files(overwrite=True)
        assert res["dockerfile_created"] is False
        assert res["compose_created"] is False

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

    installer = Installer(target_directory=str(tmp_path))
    with patch("os.makedirs", side_effect=Exception("Permission denied")):
        res = installer.setup_directories()
        assert len(res) == 0
    with patch.object(Installer, "verify_environment", return_value={"success": False}):
        res = installer.install()
        assert res["success"] is False
        assert "Environment verification failed" in res["message"]
    with patch("builtins.open", side_effect=OSError("Cannot open file")):
        res = installer.install()
        assert res["success"] is True
        assert res["config_created"] is False

    builder = PackageBuilder()
    res = builder.build_package(name=None)
    assert res["success"] is False
    assert res["package_name"] == ""
