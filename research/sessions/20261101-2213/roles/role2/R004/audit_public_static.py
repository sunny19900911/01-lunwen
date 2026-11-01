"""Independent frame assembly from strain-energy quadrature; static only."""
from pathlib import Path
import csv, hashlib, json, re
import numpy as np

O = Path(__file__).resolve().parent
S = O.parents[2]
SRC = S / 'roles/role3/R002'
PROD = S / 'roles/role6/R002'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def relative(a, b):
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))


def element_by_energy(E, area, inertia, xy0, xy1):
    direction = xy1 - xy0
    length = np.linalg.norm(direction)
    # Derivatives of axial linear and bending cubic Hermite shape functions.
    axial = np.array([-1., 0., 0., 1., 0., 0.]) / length
    local = E * area * length * np.outer(axial, axial)
    for xi in [.5 - 1 / (2 * np.sqrt(3)), .5 + 1 / (2 * np.sqrt(3))]:
        curvature = np.array([0., (-6 + 12 * xi) / length ** 2,
            (-4 + 6 * xi) / length, 0., (6 - 12 * xi) / length ** 2, (-2 + 6 * xi) / length])
        local += E * inertia * length / 2 * np.outer(curvature, curvature)
    axis = direction / length
    transverse = np.array([-axis[1], axis[0]])
    rotation = np.eye(6)
    for off in [0, 3]:
        rotation[off:off + 2, off:off + 2] = np.stack([axis, transverse])
    return rotation.T @ local @ rotation


def main():
    assert not (O / 'results.json').exists()
    freeze = json.loads((PROD / 'freeze.json').read_text(encoding='utf-8'))
    for name, data in freeze['files'].items():
        p = PROD / name; assert p.stat().st_size == data['bytes'] and sha(p) == data['sha256']
    source = json.loads((SRC / 'assembly-inputs.json').read_text())
    upstream = json.loads((PROD / 'assembled-v001/static-interface.json').read_text())
    settings = S / 'public-benchmark-settings-freeze-v001.json'
    assert sha(settings) == freeze['root_settings_sha256']
    assert sha(SRC / 'assembly-inputs.json') == freeze['input_sha256']
    source_manifest = json.loads((SRC / 'source-manifest.json').read_text())
    source_hashes = []
    for name in ['Ex5.Frame2D.build.ElasticSection.tcl', 'LibUnits.tcl']:
        p = SRC / 'local-cache' / name; d = next(x for x in source_manifest if x['file'] == name)
        assert sha(p) == d['sha256']; source_hashes.append({'name': name, 'sha256': sha(p)})
    # Parse topology/constraints directly from source Tcl text; never execute Tcl.
    text = (SRC / 'local-cache/Ex5.Frame2D.build.ElasticSection.tcl').read_text()
    node_tuples = re.findall(r'^node\s+(\d+)\s+\$X(\d)\s+\$Y(\d)', text, re.M)
    coords = {int(tag): np.array([288. * (int(x) - 1), 168. * (int(y) - 1)]) for tag, x, y in node_tuples}
    assert len(coords) == 16
    assert all(np.array_equal(coords[n['tag']], [n['x_in'], n['y_in']]) for n in source['nodes'])
    fixes = [(int(n), int(a), int(b), int(c)) for n, a, b, c in re.findall(r'^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)', text, re.M)]
    assert fixes == [(n, 1, 1, 0) for n in [11, 12, 13, 14]]
    elems = [(int(tag), int(a), int(b), sec) for tag, a, b, sec in re.findall(
        r'^element\s+nonlinearBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+\$np\s+\$(Col|Beam)SecTag', text, re.M)]
    assert len(elems) == 21
    assert {(tag, a, b, 'column' if sec == 'Col' else 'beam') for tag, a, b, sec in elems} == {
        (d['tag'], d['i'], d['j'], d['section']) for d in source['elements']}
    active = [line.split('#')[0].strip() for line in text.splitlines()]
    assert not any(line.startswith(('equalDOF ', 'rigidDiaphragm ')) for line in active)
    assert 'set ColTransfType Linear' in text and 'section Elastic' in text
    assert re.search(r'set\s+np\s+5;', text)
    assert source['E_kip_per_in2'] == 29000
    assert source['sections'] == {'column': {'A_in2': 33.5, 'Iz_in4': 4090}, 'beam': {'A_in2': 27.7, 'Iz_in4': 2700}}
    # Independent unit arithmetic, deriving nodal masses by counting half-member weights.
    g = 32.2 * 12
    wcol = 114 / 1000 / 12 * 168
    wbeam = (150 / 1000 / 12 ** 3 * 6 * 288 + 94 / 1000 / 12) * 288
    nodal = {}
    for line in active:
        match = re.match(r'mass\s+(\d+)\s+\[expr\s+(.+?)\]\s+0\.\s+0\.', line)
        if match:
            tag = int(match[1]); expr = match[2]
            nodal[tag] = (expr.count('$WeightCol/2') * wcol / 2 + expr.count('$WeightBeam/2') * wbeam / 2) / g
    assert len(nodal) == 12
    mass_error = max(abs(nodal[d['node']] - d['mx_kip_s2_per_in']) for d in source['nodal_masses'])
    tags = sorted(coords); index = {tag: j for j, tag in enumerate(tags)}
    K = np.zeros((48, 48)); M = np.zeros((48, 48)); cut = np.zeros((3, 48)); cut_members = []
    for tag, ni, nj, sec in elems:
        area, inertia = (33.5, 4090.) if sec == 'Col' else (27.7, 2700.)
        ke = element_by_energy(29000., area, inertia, coords[ni], coords[nj])
        dofs = [3 * index[ni] + j for j in range(3)] + [3 * index[nj] + j for j in range(3)]
        K[np.ix_(dofs, dofs)] += ke
        if sec == 'Col':
            level = int(coords[nj][1] / 168) - 1
            cut[level, dofs] += ke[3]
            cut_members.append({'element': tag, 'story': level + 1, 'node_i': ni, 'node_j': nj, 'end': 'j', 'component': 'global_x', 'sign': 1})
    for tag, value in nodal.items(): M[3 * index[tag], 3 * index[tag]] = value
    fixed = [3 * index[tag] + j for tag, a, b, c in fixes for j, val in enumerate([a, b, c]) if val]
    free = [j for j in range(48) if j not in fixed]
    massive = [j for j in free if M[j, j] > 0]; massless = [j for j in free if M[j, j] == 0]
    assert [len(free), len(massive), len(massless)] == [40, 12, 28]
    assert all(3 * index[tag] + 2 in massless for tag in [11, 12, 13, 14])
    kzz = K[np.ix_(massless, massless)]
    scale = np.sqrt(np.diag(kzz)); ks = kzz / np.outer(scale, scale)
    assert np.linalg.matrix_rank(ks) == 28 and np.linalg.eigvalsh(ks)[0] > 0
    H = np.zeros((48, 12)); H[massive] = np.eye(12)
    H[massless] = -np.linalg.solve(kzz, K[np.ix_(massless, massive)])
    kc = H.T @ K @ H; mc = H.T @ M @ H
    chol = np.linalg.cholesky(mc)
    dinv = np.linalg.inv(chol)
    lam, eigvectors = np.linalg.eigh(dinv @ kc @ dinv.T)
    phi = np.linalg.solve(chol.T, eigvectors); omega = np.sqrt(lam)
    pp = np.array(upstream['Phi12']); mm = np.array(upstream['M12'])
    overlap = np.diag(pp.T @ mc @ phi)
    phi *= np.where(overlap < 0, -1, 1)
    mac = (pp.T @ mc @ phi) ** 2
    fullphi = H @ phi
    selector = np.array([[float(coords[tags[d // 3]][1] >= y) for d in massive] for y in [168, 336, 504]])
    gamma = phi.T @ mc @ np.ones(12)
    ll = selector @ mc @ phi; B = ll * gamma; C = cut @ H
    modalchecks = []
    residual = K @ fullphi - (M @ fullphi) * lam
    for j in range(12):
        modalchecks.append({'mode': j + 1, 'omega_rad_s': float(omega[j]), 'period_s': float(2 * np.pi / omega[j]),
            'source_omega_relative_error': float(abs(omega[j] / upstream['omega12'][j] - 1)),
            'MAC_to_source': float(mac[j, j]),
            'full_free_equation_relative_residual': float(np.linalg.norm(residual[free, j]) / np.linalg.norm((M @ fullphi)[free, j] * lam[j])),
            'Gamma': float(gamma[j]), 'effective_mass': float(gamma[j] ** 2)})
    assert cut_members == upstream['cut_members']
    assert [f'{tags[d // 3]}.ux' for d in massive] == upstream['dof_order']
    fullselector = np.zeros((3, 48)); fullselector[:, massive] = selector
    # Independent physical sign check: +1 kip load at a roof node, no dynamic response.
    force = np.zeros(12); force[-1] = 1.
    u = np.linalg.solve(kc, force); uf = H @ u; storyforce = C @ u
    supportforce = float(np.sum((K @ uf)[[3 * index[tag] for tag in [11, 12, 13, 14]]]))
    # Static acceleration-shaped load; cut force equals mass above times 1 in/s^2.
    load_mass = mc @ np.ones(12); um = np.linalg.solve(kc, load_mass)
    a = np.array([-2., .3, 1.7, -.8, 2.2, -1.1, .6, -3., .5, 1.9, -2.7, .4])
    changed = phi * a; changedmass = np.diag(changed.T @ mc @ changed)
    changedgamma = (changed.T @ mc @ np.ones(12)) / changedmass
    changedB = (selector @ mc @ changed) * changedgamma
    result = {'source_output_files_SHA_verified': len(freeze['files']), 'cached_Tcl_sources': source_hashes,
        'source_assembly_sha256': sha(SRC / 'assembly-inputs.json'), 'root_settings_sha256': sha(settings),
        'full_free_positive_mass_massless_dimensions': [48, 40, 12, 28],
        'all_four_base_rotations_free': True, 'no_floor_merging': True,
        'Kzz_scaled_rank': int(np.linalg.matrix_rank(ks)), 'Kzz_scaled_min_eigenvalue': float(np.linalg.eigvalsh(ks)[0]),
        'Kzz_scaled_condition2': float(np.linalg.cond(ks)),
        'mass_source_arithmetic_max_abs_error': mass_error, 'total_mass_kip_s2_per_in': float(np.sum(np.diag(mc))),
        'M12_max_abs_difference': float(np.max(abs(mc - mm))),
        'K12_relative_difference': relative(kc, np.array(upstream['K12'])),
        'C3x12_relative_difference': relative(C, np.array(upstream['C3x12'])),
        'B3x12_max_abs_difference_kip_s2_per_in': float(np.max(abs(B - np.array(upstream['B3x12'])))),
        'modal_omega_max_relative_difference': max(d['source_omega_relative_error'] for d in modalchecks),
        'modal_MAC_min': float(np.min(np.diag(mac))),
        'full_free_eigen_max_column_relative': max(d['full_free_equation_relative_residual'] for d in modalchecks),
        'cut_vs_upper_domain_equilibrium_relative': relative(cut, fullselector @ K),
        'cut_modal_vs_omega2_L_relative': relative(C @ phi, ll * lam),
        'modal_mass_orthogonality_max_abs_error': float(np.max(abs(phi.T @ mc @ phi - np.eye(12)))),
        'complete_effective_mass_relative_error': float(abs(np.sum(gamma ** 2) / np.sum(np.diag(mc)) - 1)),
        'B_sign_scale_invariance_max_absolute_error': float(np.max(abs(changedB - B))),
        'sum_B_equals_mass_above_max_absolute_error': float(np.max(abs(B.sum(axis=1) - selector @ mc @ np.ones(12)))),
        'roof_unit_load_cut_forces_kip': storyforce.tolist(), 'roof_unit_load_support_x_reaction_kip': supportforce,
        'roof_unit_load_cut_max_error_kip': float(np.max(abs(storyforce - 1))),
        'unit_acceleration_static_cut_max_error_kip': float(np.max(abs(C @ um - selector @ load_mass))),
        'first_period_s': modalchecks[0]['period_s'],
        'units_contract': 'ag in/s2; s in; B kip*s2/in; V=sum(B*omega^2*s) kip; no /1000 and no second Gamma',
        'scope': 'independent Euler-Bernoulli strain-energy static reconstruction; no OpenSees execution, record read or dynamic response'}
    assert result['K12_relative_difference'] < 1e-10 and result['C3x12_relative_difference'] < 1e-10
    assert result['B3x12_max_abs_difference_kip_s2_per_in'] < 1e-10
    assert result['modal_omega_max_relative_difference'] < 1e-10 and result['modal_MAC_min'] > 1 - 1e-10
    assert result['cut_modal_vs_omega2_L_relative'] < 1e-10
    assert result['roof_unit_load_cut_max_error_kip'] < 1e-10 and abs(supportforce + 1) < 1e-10
    with (O / 'modal-independent-checks-12.csv').open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(modalchecks[0])); w.writeheader(); w.writerows(modalchecks)
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
