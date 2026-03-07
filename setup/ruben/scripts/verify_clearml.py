"""
verify_clearml.py — Verify ClearML credentials and workspace connectivity.
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def verify():
    try:
        from clearml import Task
    except ImportError:
        print("✗ clearml package not installed. Run: pip install clearml")
        sys.exit(1)

    # Check config file or env vars
    conf_path = os.path.expanduser("~/clearml.conf")
    has_conf = os.path.isfile(conf_path)
    has_env = bool(os.getenv("CLEARML_API_ACCESS_KEY"))

    if not has_conf and not has_env:
        print("✗ No ClearML config found.")
        print("  Run scripts/setup_clearml.sh or set env vars in .env")
        sys.exit(1)

    source = "~/clearml.conf" if has_conf else "environment variables"
    print(f"  Config source: {source}")
    print("  Connecting to ClearML server...")

    try:
        task = Task.init(
            project_name="Setup Verification",
            task_name="verify_connection",
            auto_connect_frameworks=False,
            output_uri=False,
        )
        task_id = task.id
        task.close()
        print(f"  Task created successfully (ID: {task_id})")
        print(f"\n✓ ClearML is configured and connected!\n")
        print(f"  View task at: https://app.clear.ml/projects/*/experiments/{task_id}\n")
    except Exception as e:
        print(f"\n✗ ClearML connection failed: {e}")
        print("  Check your credentials and server URL in ~/clearml.conf\n")
        sys.exit(1)


if __name__ == "__main__":
    print("\n── ClearML Verification ───────────────────────")
    try:
        verify()
    except SystemExit:
        raise
    except Exception as e:
        print(f"\n✗ ClearML verification failed: {e}\n")
        sys.exit(1)
