import subprocess
import sys
import os

def test_cli_version():
    # Run qcc --version via python -m qcc.main --version
    result = subprocess.run(
        [sys.executable, "-m", "qcc.main", "--version"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": os.path.join(os.getcwd(), "src")}
    )
    assert "QCC" in result.stdout or result.returncode == 0
