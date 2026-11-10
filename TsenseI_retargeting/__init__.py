"""Standalone MediaPipe-21 TsenseIRetarget package."""

from .landmarks import (
    FINGER_CHAINS,
    LANDMARK_NAMES,
    NUM_LANDMARKS,
    PINCH_PAIRS,
    TIP_IDS,
    WRIST_ID,
    palm_width_m,
    points21,
)
from .tsensei_retarget import (
    TsenseIRetarget,
    TsenseIRetargetConfig,
    TsenseIRetargetResult,
    load_mediapipe_record_points,
    resolve_robot_root,
    retarget_mediapipe_landmarks,
)

# Compatibility for existing integrations; the new names are the canonical API.
TopoRetargeter = TsenseIRetarget
TopoRetargetConfig = TsenseIRetargetConfig
TopoRetargetResult = TsenseIRetargetResult

__all__ = [
    "FINGER_CHAINS",
    "LANDMARK_NAMES",
    "NUM_LANDMARKS",
    "PINCH_PAIRS",
    "TIP_IDS",
    "TsenseIRetarget",
    "TsenseIRetargetConfig",
    "TsenseIRetargetResult",
    "TopoRetargeter",
    "TopoRetargetConfig",
    "TopoRetargetResult",
    "WRIST_ID",
    "load_mediapipe_record_points",
    "palm_width_m",
    "points21",
    "resolve_robot_root",
    "retarget_mediapipe_landmarks",
]
