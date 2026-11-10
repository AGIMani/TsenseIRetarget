# TsenseI_retargeting

The **TsenseIRetarget** solver maps MediaPipe-order 21-point hand landmarks to
robot joint angles. Former TopoRetarget imports remain available as compatibility
aliases. This repository snapshot provides TsenseI A3.2 and A3.2 with ID
assets for both hands under `assets/hands/`.

## Install and run

Follow the [root README](../README.md) to create the Python environment. From
the repository root, run the A3.2 example:

```bash
.venvs/track/bin/python examples/retarget_a32.py --model TsenseI_v3_2_withid --side left
```

For Python use, load a model profile and create a side-specific solver:

```python
import sys
sys.path[:0] = [".", "src"]
from hand_profiles import load_hand_profile

solver = load_hand_profile("TsenseI_v3_2_withid").create_retargeter("left")
points = solver.fk.compute()  # example: neutral-pose landmarks
result = solver.retarget(points)
print(result.joint_values)    # URDF joint name -> radians
```

Inputs are `21 × 3` metric coordinates in the solver's wrist frame, in
MediaPipe Hands order. Use the root example's `--source-frame mediapipe`
option for the web application's MediaPipe input conversion. Reuse a solver
for successive frames to retain its warm start. See the root README for model
calibration limitations and the web preview.

## Landmark order

| IDs | Name |
| --- | --- |
| 0 | Wrist |
| 1–4 | Thumb CMC to tip |
| 5–8 | Index MCP to tip |
| 9–12 | Middle MCP to tip |
| 13–16 | Ring MCP to tip |
| 17–20 | Little MCP to tip |

Palm width uses the distance between Index MCP and Little MCP (5 and 17).
Pixel or normalized image coordinates require metric reconstruction and the
appropriate coordinate transform before solving.

## Layout and other robots

The public API is in `__init__.py`, the solver is in `tsensei_retarget.py`,
and forward kinematics are under `fk/`. Model packages contain a URDF,
meshes, keypoint YAML and evaluation configuration. To use a different robot,
provide a compatible model package and configure `TsenseIRetargetConfig`
explicitly; see the implementation and existing A3.2 profiles for the expected
configuration.

## Notes

- Five independent fingertip position targets (MediaPipe 4/8/12/16/20) are
  enabled by default. Each coefficient comes from the selected robot keypoint
  YAML's `weight` (2.0 in the current assets); the schema file is descriptive.
  Source points are wrist-centered, scaled to robot palm width, and expressed
  in their palm frame. Robot points use the fixed neutral-pose palm frame.
  The added loss is `0.5 * lambda_fingertip * sum(weight_i * ||tip_i-target_i||² / palm_width²)`.
  During pinch, each partner's position coefficient is multiplied by `1-alpha`;
  the thumb uses `1-max(alpha)` across its four contacts. This continuously
  releases conflicting absolute targets as contact takes priority, restoring
  the full coefficient on release. Uninvolved fingers keep their position weight.
  Residuals use `sqrt(weight_i)`, so 2.0 doubles the squared-error coefficient.
  `lambda_fingertip=1.0` is the default overall multiplier; set it to 0 to disable
  this term. Per-tip zero weights also disable the respective contribution;
  negative/nonfinite weights are rejected. Initialization-only mode omits it.
  Analytic Jacobians, finite differences, line search and loss reporting use
  the same objective. `loss["fingertip_position_weighted"]` reports its contribution;
  diagnostics report the configured weights and whether this term is active.
  This soft objective trades off with topology, bone direction and pinch terms;
  actual camera accuracy and calibrated robot reachability still limit tracking.
- Thumb contact with each of the four fingers (MediaPipe 4–8/12/16/20) is enabled
  by default: `pinch_full_ratio=0.15`,
  `pinch_start_ratio=0.50`, `pinch_weight=65.0`. The current input's 5–17 palm width
  sets both thresholds; each pair independently applies smoothstep to its own
  distance and blends its normalized FK contact residual. Multiple close tips
  can be active together; releasing a pair removes its contact residual.
  Set `pinch_enabled=False` to disable contact without disabling fingertip tracking. Contact is also
  inactive when `use_topo_optimization=False` or the weight is zero.
- `result.diagnostics["pinch"]["pairs"]` reports each finger's gap, ratio and
  activation under `index`, `middle`, `ring`, and `pinky`. The scalar gap/ratio/
  activation fields in `diagnostics["pinch"]` retain the original index meaning;
  palm width and the start threshold are shared by all pairs. Each model's
  `retarget.pinch_index_full_ratio` independently sets the thumb/index full
  activation threshold; `pinch_full_ratio` sets it for the other three fingers.
  Both must satisfy `0 <= full < pinch_start_ratio`. Omitted/null index full
  ratio inherits `pinch_full_ratio` for older configurations. Per-pair diagnostics
  report `full_ratio` and `full_threshold_m`; the top-level threshold follows index.
  Each registered model has
  its own `retarget.pinch_index_weight` for thumb/index contact (4-8), initialized
  from its existing contact weight; `pinch_weight` controls the other three pairs.
  Raising `pinch_index_weight` strengthens only the index contact objective.
  Zero disables only that pair; omitted/null inherits `pinch_weight` for older
  configurations. Per-pair diagnostics include the effective `weight`;
  the top-level weight follows index. This is independent of the fingertip
  position-tracking YAML weight of 2.0.
  `include_artifacts=True` additionally reports the solved gap and contact loss.
  Contact uses calibrated keypoints and remains a soft objective, so a requested
  zero gap is not guaranteed by every model/pose. Existing joint limits, iteration
  budgets and downstream collision/trajectory handling still apply.
- Algorithm is native MediaPipe-21 topology (not Quest-26).
- Pinocchio is optional; without it the solver uses finite-difference Jacobians.
