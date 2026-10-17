"""Refine one archived physical three-storey model; no broad model search.

Baseline 360-point log grid, then a 200001-point grid and bounded golden searches.
Direct physical-coordinate solves independently check all six peak candidates.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import platform
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT.parent / 'W5-重燃双塔连体/02-数据/理论解析突破-20261016'
OUT = Path(__file__).resolve().parent / 'round002'
Z0, Z1 = .05, .08


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def golden_max(function, left, right, iterations=90):
    # Search in log-frequency to retain scale invariance.
    a, b = np.log(left), np.log(right)
    g = (np.sqrt(5.) - 1.) / 2
    c, d = b - g * (b-a), a + g * (b-a)
    fc, fd = function(np.exp(c)), function(np.exp(d))
    for _ in range(iterations):
        if fc < fd:
            a, c, fc = c, d, fd
            d = a + g * (b-a)
            fd = function(np.exp(d))
        else:
            b, d, fd = d, c, fc
            c = b - g * (b-a)
            fc = function(np.exp(c))
    candidates = [(left, function(left)), (right, function(right)),
                  (np.exp(c), fc), (np.exp(d), fd)]
    return max(candidates, key=lambda x: x[1])


def main():
    started = time.perf_counter()
    OUT.mkdir(exist_ok=True)
    src = SOURCE / 'physical_three_story_search.json'
    old_script = SOURCE / 'search_physical_three_story.py'
    archive = json.loads(src.read_text(encoding='utf-8'))
    m, k = np.array(archive['mass']), np.array(archive['stiffness'])
    M = np.diag(m)
    B = np.array([[1., 0, 0], [-1, 1, 0], [0, -1, 1.]])
    K = B.T @ np.diag(k) @ B
    scale = np.diag(1 / np.sqrt(m))
    eigenvalues, Q = np.linalg.eigh(scale @ K @ scale)
    omega = np.sqrt(eigenvalues)
    Phi = scale @ Q
    gamma = Phi.T @ M @ np.ones(3)
    outputs = np.vstack([np.diag(k) @ B, K])
    labels = ['cut1', 'cut2', 'cut3', 'net1', 'net2', 'net3']
    residues = -(outputs @ Phi) * gamma[None, :]

    def modal(freq, damping):
        freq = np.asarray(freq)
        den = eigenvalues - freq[..., None]**2 + 2j * damping * freq[..., None] * omega
        return (1 / den) @ residues.T

    def ratio(freq):
        return abs(modal(freq, Z1)) / abs(modal(freq, Z0))

    def C(damping):
        return M @ Phi @ np.diag(2 * damping * omega) @ Phi.T @ M

    def physical(freq, damping):
        dynamic = K - freq**2 * M + 1j * freq * C(damping)
        rhs = -M @ np.ones(3)
        u = np.linalg.solve(dynamic, rhs)
        return outputs @ u, float(np.linalg.norm(dynamic @ u - rhs) / np.linalg.norm(rhs))

    lo, hi = .7 * omega[0], 1.5 * omega[-1]
    original_grid = np.exp(np.linspace(np.log(lo), np.log(hi), 360))
    fine_grid = np.exp(np.linspace(np.log(lo), np.log(hi), 200001))
    r_coarse, r_fine = ratio(original_grid), ratio(fine_grid)
    old_index = labels.index(archive['output'])
    old_modal = [modal(archive['Omega'], damping)[old_index] for damping in [Z0, Z1]]
    old_direct = [physical(archive['Omega'], damping)[0][old_index] for damping in [Z0, Z1]]
    archive_reproduction = {
        'frequency_rad_s': archive['Omega'], 'ratio_archived': archive['ratio'],
        'ratio_recomputed_modal': float(abs(old_modal[1]) / abs(old_modal[0])),
        'ratio_recomputed_physical': float(abs(old_direct[1]) / abs(old_direct[0])),
        'H0_abs_archived': archive['H0_abs'], 'H1_abs_archived': archive['H1_abs'],
        'H0_abs_physical': float(abs(old_direct[0])), 'H1_abs_physical': float(abs(old_direct[1])),
        'residue_max_abs_difference': float(np.max(abs(residues[old_index] - np.array(archive['residues'])))),
    }

    maxima, local_candidates = [], []
    for j, label in enumerate(labels):
        ri = r_fine[:, j]
        peaks = np.flatnonzero((ri[1:-1] >= ri[:-2]) & (ri[1:-1] >= ri[2:])) + 1
        candidates = [(float(fine_grid[0]), float(ri[0])), (float(fine_grid[-1]), float(ri[-1]))]
        for index in peaks:
            f, r = golden_max(lambda x: float(ratio(x)[j]), fine_grid[index-1], fine_grid[index+1])
            candidates.append((float(f), float(r)))
            local_candidates.append({'output': label, 'bracket_lo_rad_s': float(fine_grid[index-1]),
                                     'bracket_hi_rad_s': float(fine_grid[index+1]),
                                     'frequency_rad_s': float(f), 'modal_ratio': float(r)})
        frequency, value = max(candidates, key=lambda pair: pair[1])
        direct0, residual0 = physical(frequency, Z0)
        direct1, residual1 = physical(frequency, Z1)
        modal0, modal1 = modal(frequency, Z0), modal(frequency, Z1)
        plus = residues[j] >= 0
        den = eigenvalues - frequency**2 + 2j * Z0 * omega * frequency
        groupplus = np.sum(residues[j, plus] / den[plus])
        groupminus = np.sum(-residues[j, ~plus] / den[~plus])
        chi = float(abs(groupplus - groupminus) / (abs(groupplus) + abs(groupminus)))
        ci = int(np.argmax(r_coarse[:, j]))
        maxima.append({'output': label, 'coarse360_max_ratio': float(r_coarse[ci, j]),
                       'coarse360_peak_frequency_rad_s': float(original_grid[ci]),
                       'dense200001_max_ratio': float(np.max(ri)), 'refined_ratio': value,
                       'refined_frequency_rad_s': frequency, 'physical_ratio': float(abs(direct1[j]) / abs(direct0[j])),
                       'H0_abs': float(abs(direct0[j])), 'H1_abs': float(abs(direct1[j])),
                       'H0_complex_relative_discrepancy': float(abs(modal0[j] - direct0[j]) / abs(direct0[j])),
                       'H1_complex_relative_discrepancy': float(abs(modal1[j] - direct1[j]) / abs(direct1[j])),
                       'physical_solve_relative_residual': max(residual0, residual1),
                       'baseline_chi': chi, 'kappa_over_chi': (Z1/Z0) / chi,
                       'residue_signs': ','.join('+' if r > 0 else '-' if r < 0 else '0' for r in residues[j]),
                       'found_local_maxima': len(peaks)})
    with (OUT/'frequency_maxima.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(maxima[0]));writer.writeheader();writer.writerows(maxima)
    # Compact data around the former best, sufficient to inspect its shape.
    window=np.linspace(archive['Omega'] * .97, archive['Omega'] * 1.03, 401)
    with (OUT/'net2_frequency_window.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['frequency_rad_s','abs_H0','abs_H1','ratio'])
        for freq in window:
            a,b=modal(freq,Z0)[old_index],modal(freq,Z1)[old_index]
            writer.writerow([float(freq),float(abs(a)),float(abs(b)),float(abs(b)/abs(a))])
    checks = {
        'M_K_positive_definite': bool(np.all(m>0) and np.min(np.linalg.eigvalsh(K))>0),
        'C0_and_added_C_positive_definite': bool(np.min(np.linalg.eigvalsh(C(Z0)))>0 and np.min(np.linalg.eigvalsh(C(Z1)-C(Z0)))>0),
        'modal_mass_orthonormal_below_1e-12': bool(np.max(abs(Phi.T@M@Phi-np.eye(3)))<1e-12),
        'archive_ratio_reproduced_below_1e-10': abs(archive_reproduction['ratio_recomputed_modal']/archive['ratio']-1)<1e-10,
        'all_refined_modal_physical_complex_matches_below_1e-8': all(max(r['H0_complex_relative_discrepancy'],r['H1_complex_relative_discrepancy'])<1e-8 for r in maxima),
        'all_direct_solve_residuals_below_1e-12': all(r['physical_solve_relative_residual']<1e-12 for r in maxima),
        'net_output_is_adjacent_cut_difference': bool(np.max(abs(K-np.array([[1,-1,0],[0,1,-1],[0,0,1]])@outputs[:3]))<1e-13),
        'elapsed_below_300_seconds': time.perf_counter()-started<300,
    }
    result={'evidence_id':'E-EXP-002','finished_utc':datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds':time.perf_counter()-started,'code_sha256':sha(__file__),
            'source_model':str(src),'source_model_sha256':sha(src),'source_search_script_sha256':sha(old_script),
            'python':platform.python_version(),'numpy':np.__version__,'python_executable':sys.executable,
            'model':{'mass':m.tolist(),'stiffness':k.tolist(),'M':M.tolist(),'K':K.tolist(),'B':B.tolist(),
                     'omega':omega.tolist(),'residues':residues.tolist(),'zeta0':Z0,'zeta1':Z1,
                     'C0':C(Z0).tolist(),'C1':C(Z1).tolist(),'added_C_eigenvalues':np.linalg.eigvalsh(C(Z1)-C(Z0)).tolist()},
            'archive_reproduction':archive_reproduction,'frequency_domain_rad_s':[float(lo),float(hi)],
            'dense_grid_n':len(fine_grid),'maxima':maxima,'local_candidates':local_candidates,'checks':checks,
            'largest_refined':max(maxima,key=lambda r:r['refined_ratio']),
            'boundary':'One fixed model and a finite frequency interval. Dense scan plus local golden refinement is not a certified global upper bound. Harmonic amplitude ratios do not establish finite-record or all-input peak ratios.'}
    (OUT/'frequency_refinement.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':checks,'largest_refined':result['largest_refined'],'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
