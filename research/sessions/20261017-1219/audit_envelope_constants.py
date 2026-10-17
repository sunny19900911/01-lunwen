"""Independent Machin-pi / Decimal audit of frozen C023 constant evaluations."""
from pathlib import Path
from decimal import Decimal as D, localcontext
import ast, csv, hashlib, json
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EXP = ROOT/'papers/damping-output-boundaries/experiments/theory-round003-envelope-constants'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def atan_reciprocal(q):
    x = D(1)/q
    result = term = x
    n = 1
    while True:
        term *= -x*x
        addition = term/(2*n+1)
        result += addition
        if abs(addition) < D('1e-105'):
            return result
        n += 1

def main():
    record = json.loads((EXP/'run_record.json').read_text('utf-8'))
    for item in record['sources']:
        assert sha(Path(item['file'])) == item['sha256']
    for item in record['files']:
        assert sha(EXP/item['file']) == item['sha256']
    ast.parse((EXP/'evaluate_constants.py').read_text('utf-8'))
    data = json.loads((EXP/'envelope_constants.json').read_text('utf-8'))
    src = json.loads((EXP.parent/'theory-round001-detuning/detuning_values.json').read_text('utf-8'))['fixed_model']
    for key, val in data['reused_original_values'].items():
        assert src[key] == val
    with localcontext() as ctx:
        ctx.prec = 100
        ws = list(map(D, src['omega'])); rs = list(map(D, src['rho']))
        S, z = D(src['S']), D(src['zeta_crit'])
        k, eta = D(8)/5, D(3)/16
        zlo, zhi = (1-eta)*z, k*(1+eta)*z
        assert 0 < zlo <= zhi < 1
        dm = dp = D(1)
        for w in ws:
            gap = S*S-w*w
            dm *= gap
            dp *= (gap**2 + (2*zhi*w*S)**2).sqrt()
        A, B = (2+eta)/dm, (k-1)*(k+3)/(4*dp)
        moment = 2*sum(abs(r)/w**3 for w,r in zip(ws,rs))/zlo**3
        pi = 16*atan_reciprocal(5)-4*atan_reciprocal(239)
        E = pi*moment/2
        vals = {'D_minus':dm, 'D_plus':dp,'A':A,'B':B,'gamma':zlo,'M':moment,'pi':pi,'E':E,'T0':2*E/B,'Tenv':E/A,'C':B/(2*A)}
        diffs = {key: abs(value/D(data['constants'][key])-1) for key,value in vals.items()}
        assert max(diffs.values()) < D('1e-80')
        rows = list(csv.DictReader((EXP/'four_crossover_durations.csv').open(encoding='utf-8')))
        assert [r['delta'] for r in rows] == ['0.1','0.01','0.001','0.0001']
        for row in rows:
            cross = vals['Tenv']/D(row['delta'])
            full = 2*max(vals['T0'],cross)
            for name, value in [('Tenv_over_delta_half_duration_s',cross),('full_input_support_2T_s',full),('crossing_half_duration_years_365_days',cross/D(31536000))]:
                assert abs(value/D(row[name])-1) < D('1e-80')
        assert datetime.fromisoformat(record['protocol_file_last_write_utc']) < datetime.fromisoformat(record['finished_utc'])
        report = {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'actual_exit':0,'sources_outputs_hashes_match':True,'independent_pi_method':'Machin arctangent series; original used Chudnovsky','max_relative_numeric_difference':str(max(diffs.values())),'four_existing_delta_rows_only':True,'T0_half_duration_days':str(vals['T0']/86400),'smallest_delta_full_support_years_365_days':str(D(rows[-1]['full_input_support_2T_s'])/31536000),'scope':'Ordinary approximate evaluation of conservative sufficient conditions, not necessary durations, actual peaks, directed intervals or spectrum error certification','source_script_not_rerun':True}
    (HERE/'envelope-constants-master-audit.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,ensure_ascii=False))
if __name__ == '__main__':
    main()
