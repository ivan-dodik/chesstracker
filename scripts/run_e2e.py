#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Convenience script to run E2E tests with Playwright.

Usage:
    python scripts/run_e2e.py              # Run all E2E tests
    python scripts/run_e2e.py test_auth.py # Run specific test file
    python scripts/run_e2e.py -k login     # Run tests matching keyword
"""

import os
import subprocess
import sys


def main():
    backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
    backend_dir = os.path.abspath(backend_dir)

    # Build pytest command — E2E tests live in backend/e2e/ (outside tests/)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "e2e/",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ]

    # Add extra arguments (e.g., specific test file or -k filter)
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        if args[0].endswith(".py") and not args[0].startswith("e2e/"):
            args[0] = f"e2e/{args[0]}"
        cmd.extend(args)

    print(f"Running E2E tests from {backend_dir}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=backend_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()