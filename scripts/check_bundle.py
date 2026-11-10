"""Check A3.2 meshes, calibration drafts and neutral-pose solves without hardware."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src'), str(ROOT / 'src/tracking'), str(ROOT / 'tools')]
from hand_profiles import A32_MODEL_IDS, load_hand_profile
from online_control.online_motion_track.calibration import CalibrationSession
from TsenseI_retargeting import TsenseIRetarget
from TsenseI_retargeting.fk.urdf import UrdfModel

for model_id in A32_MODEL_IDS:
    for side in ('left', 'right'):
        profile = load_hand_profile(model_id)
        model = UrdfModel(profile.path('urdf', side))
        missing = model.missing_meshes()
        if missing:
            raise RuntimeError(f'{model_id}/{side}: missing meshes: {missing}')
        if len(profile.joint_limits(side)) != 20:
            raise RuntimeError(f'{model_id}/{side}: expected 20 joints')
        solver = profile.create_retargeter(side)
        result = solver.retarget(solver.fk.compute(), include_artifacts=False)
        if not isinstance(solver, TsenseIRetarget) or not result.success or len(result.joint_values) != 20:
            raise RuntimeError(f'{model_id}/{side}: retarget solve failed')
        session = CalibrationSession(side, model_id=model_id)
        try:
            if len(session.data['keypoints']) != 21:
                raise RuntimeError(f'{model_id}/{side}: expected 21 calibration points')
            draft = deepcopy(session.data['keypoints'])
            draft[8]['local_xyz'][0] += .001
            updated = session.update({'calibration_rows': draft, 'preset': 'pinch_index'})
            if not np.isfinite(updated['result_points']).all() or not session.export({})['yaml']:
                raise RuntimeError(f'{model_id}/{side}: calibration preview failed')
            with tempfile.TemporaryDirectory(prefix='tsensei-calibration-check-') as folder:
                session.path = Path(folder) / 'points.yaml'
                session.path.write_bytes(profile.path('keypoints', side).read_bytes())
                saved = session.save({})
                if not Path(saved['backup']).is_file():
                    raise RuntimeError(f'{model_id}/{side}: calibration backup failed')
        finally:
            session.close()
        print(f'OK {model_id} / {side}: meshes, 21 points, solve, preview and temporary save')
print('校验通过；未连接或控制机械手。')
