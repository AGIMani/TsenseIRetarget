#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PYTHON="$ROOT/.venvs/track/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  printf '%s\n' '请先创建 .venvs/track 并安装 requirements.txt（见 README.md）。' >&2
  exit 1
fi
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE CONDA_PREFIX CONDA_DEFAULT_ENV VIRTUAL_ENV WUJI_BRIDGE_URL
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd -- "$ROOT"
printf '%s\n' '动态标定：http://127.0.0.1:8766/calibration'
exec "$PYTHON" online_control/online_motion_track/server.py --host 127.0.0.1 --port 8766 --no-open "$@"
