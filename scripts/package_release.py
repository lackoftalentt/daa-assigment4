#!/usr/bin/env python3
"""Package committed deliverables and a runnable JAR without build caches or Git internals."""
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "DAA_Assignment4_Beibarys_Balykbayev_SE-2516.zip"


def package():
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
        raise SystemExit("Commit the final deliverables before creating a release archive.")
    jar = ROOT / "target/daa-assignment4-1.0.jar"
    if not jar.exists():
        raise SystemExit("Run mvn verify first.")
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    destination = ROOT.parent / NAME
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in sorted(filter(None, files)):
            archive.write(ROOT / relative, "daa-assigment4/" + relative)
        archive.write(jar, "daa-assigment4/bin/daa-assignment4-1.0.jar")
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise SystemExit("Archive integrity check failed")
    print(f"Created {destination} ({destination.stat().st_size:,} bytes)")


if __name__ == "__main__":
    package()
