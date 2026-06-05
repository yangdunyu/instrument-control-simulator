import os

# Disable random errors and delays for deterministic tests.
# The deployed app reads SIMULATE_ERRORS=true from the environment.
os.environ.setdefault("SIMULATE_ERRORS", "false")
