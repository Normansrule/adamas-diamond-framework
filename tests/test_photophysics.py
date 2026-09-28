import json
import shutil
import subprocess
from pathlib import Path

import pytest

from adamas import photophysics as P

WEB = Path(__file__).resolve().parents[1] / "web"


def test_bright_state_and_polarization():
    assert 0.3 < P.readout_contrast() < 0.55           # ms=0 is brighter in the first few hundred ns
    assert 0.75 < P.polarization() < 0.95               # light pumps the spin into ms=0
    early0, early1 = P.fluorescence(1.0, "0", 0.05)[0], P.fluorescence(1.0, "1", 0.05)[0]
    assert early0 > 2 * early1


@pytest.mark.skipif(shutil.which("node") is None, reason="node missing")
def test_photon_lab_matches_python(tmp_path):
    js = tmp_path / "c.mjs"
    js.write_text(f"import * as PH from '{(WEB / 'assets/sim/photophys.js').as_uri()}'; console.log(JSON.stringify([0.3, 1, 2].map(b => PH.contrast(b, 0.3))));")
    got = json.loads(subprocess.run(["node", str(js)], capture_output=True, text=True, check=True).stdout)
    for b, g in zip([0.3, 1, 2], got):
        assert abs(g - P.readout_contrast(b, 0.3)) < 0.01
