"""The renamed solver stays compatible with existing integrations."""
import importlib
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from hand_profiles import A32_MODEL_IDS, load_hand_profile
from TsenseI_retargeting import (
    TsenseIRetarget,
    TsenseIRetargetConfig,
    TsenseIRetargetResult,
    TopoRetargeter,
    TopoRetargetConfig,
    TopoRetargetResult,
)


def test_legacy_imports_share_the_same_classes_and_module():
    old = importlib.import_module("TsenseI_retargeting.toporetarget")
    current = importlib.import_module("TsenseI_retargeting.tsensei_retarget")
    assert old is current
    assert old.TopoRetargeter is TopoRetargeter is TsenseIRetarget
    assert old.TopoRetargetConfig is TopoRetargetConfig is TsenseIRetargetConfig
    assert old.TopoRetargetResult is TopoRetargetResult is TsenseIRetargetResult


@pytest.mark.parametrize("model_id", A32_MODEL_IDS)
@pytest.mark.parametrize("side", ("left", "right"))
def test_a32_profiles_use_renamed_solver(model_id, side):
    solver = load_hand_profile(model_id).create_retargeter(side)
    result = solver.retarget(solver.fk.compute(), include_artifacts=False)
    assert type(solver) is TsenseIRetarget
    assert isinstance(result, TsenseIRetargetResult)
    assert result.success and result.diagnostics["algorithm"] == "TsenseIRetarget"
