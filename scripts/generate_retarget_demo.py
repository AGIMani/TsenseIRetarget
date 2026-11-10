"""Generate the synthetic inputs and actual solver outputs used in the demo.

Run from the repository root with the dependencies in requirements.txt:
    .venvs/track/bin/python scripts/generate_retarget_demo.py

The output records a sequence of model-derived calibration presets, not camera
or robot hardware data. Each frame is solved by the same CalibrationSession
used by the web application, with its warm start retained across frames.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src'), str(ROOT / 'tools')]

from keypoint_pose_presets import make_preset, model_flexion_hint
from online_control.online_motion_track.calibration import CalibrationSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/retarget-demo-frames.json')
    args = parser.parse_args()
    fps = 20
    session = CalibrationSession('left', model_id='TsenseI_v3_2_withid')
    try:
        reference = session.world_points()
        hint = model_flexion_hint(session.engine.solver.fk.model, session.data['keypoints'])
        frames = []

        def add(points, label):
            result = session.update({'input_points': points.tolist()})
            frames.append({
                'label': label,
                'input_points': np.round(points, 6).tolist(),
                'joint_values': {name: round(value, 6) for name, value in result['pose'].items()},
            })

        for _ in range(12):
            add(reference, 'Neutral')
        for preset, label in [('fist', 'Fist'), ('pinch_index', 'Index pinch'),
                              ('pinch_middle', 'Middle pinch')]:
            target = make_preset(reference, preset, hint).points
            for index in range(1, 21):
                t = index / 20
                t = t * t * (3 - 2 * t)
                add(reference * (1 - t) + target * t, label)
            for _ in range(10):
                add(target, label)
            for index in range(1, 21):
                t = index / 20
                t = t * t * (3 - 2 * t)
                add(target * (1 - t) + reference * t, label)
            for _ in range(10):
                add(reference, 'Neutral')
    finally:
        session.close()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        'description': 'Synthetic calibration preset input; no camera or robot hardware.',
        'model': 'TsenseI_v3_2_withid', 'side': 'left', 'fps': fps, 'frames': frames,
    }, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f'Wrote {len(frames)} solved frames at {fps} fps to {args.output}')


if __name__ == '__main__':
    main()
