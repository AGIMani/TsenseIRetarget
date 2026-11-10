"""Run one A3.2 solve using the same profile as the web application."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from hand_profiles import load_hand_profile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model', choices=['TsenseI_v3_2', 'TsenseI_v3_2_withid'], default='TsenseI_v3_2_withid')
parser.add_argument('--side', choices=['left', 'right'], default='left')
parser.add_argument('--input-json', type=Path, help='21 x 3 metric points in a JSON array')
parser.add_argument('--source-frame', choices=['wrist', 'mediapipe'], default='wrist',
                    help='wrist: solver wrist frame; mediapipe: apply the web input transform')
args = parser.parse_args()
solver = load_hand_profile(args.model).create_retargeter(args.side)
if args.input_json:
    import numpy as np
    points = np.asarray(json.loads(args.input_json.read_text(encoding='utf-8')), dtype=float)
    if args.source_frame == 'mediapipe':
        from online_control.online_motion_track.pipeline_v3_2.pipeline import prepare_points
        points = prepare_points(points, args.side)
else:
    points = solver.fk.compute()
result = solver.retarget(points, include_artifacts=False)
if not result.success:
    raise SystemExit('求解未成功，请检查输入关键点与标定。')
print(json.dumps({'model': args.model, 'side': args.side, 'algorithm': result.diagnostics['algorithm'],
                  'unit': 'radian', 'joint_values': result.joint_values}, ensure_ascii=False, indent=2))
