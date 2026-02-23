"""
Script setup môi trường ảo và cài đặt dependencies.
Chạy: python setup_venv.py
(Sử dụng Python hệ thống, không cần kích hoạt venv trước.)
"""
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent
    venv_path = project_root / ".venv"
    requirements = project_root / "requirements.txt"

    if not requirements.exists():
        print("Không tìm thấy requirements.txt.")
        sys.exit(1)

    if venv_path.exists():
        print(".venv đã tồn tại. Đang cài đặt/cập nhật dependencies...")
    else:
        print("Đang tạo môi trường ảo (.venv)...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            cwd=project_root,
        )
        print("Đã tạo .venv.")

    pip = venv_path / "Scripts" / "pip.exe" if os.name == "nt" else venv_path / "bin" / "pip"
    if not pip.exists():
        pip = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"

    print("Đang cài đặt packages từ requirements.txt...")
    result = subprocess.run(
        [str(pip), "install", "-r", str(requirements)],
        cwd=project_root,
    )
    if result.returncode != 0:
        print("Cài đặt thất bại.")
        sys.exit(result.returncode)

    print("Setup xong. Kích hoạt môi trường ảo:")
    if os.name == "nt":
        print("  .venv\\Scripts\\activate")
        print("Rồi chạy bot: python main.py")
    else:
        print("  source .venv/bin/activate")
        print("Rồi chạy bot: python main.py")


if __name__ == "__main__":
    main()
