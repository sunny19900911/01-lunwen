"""Exact fixed-summary rank audit by half-line intersection, not root-cell reuse."""
import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from fractions import Fraction as Q
from pathlib import Path

AHAT=Q('2.0006042528243313e-6')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def weak_order(values):
    levels=defaultdict(list)
    for name,value in values.items():levels[value].append(name)
    return [sorted(levels[v]) for v in sorted(levels,reverse=True)]


def selected(values):
    levels=sorted(values.values(),reverse=True)
    return (tuple(sorted(k for k,v in values.items() if v>=levels[1])),
            tuple(sorted(k for k,v in values.items() if v<=levels[-2])))


def scores(items,a):return {name:w-a*h for name,(w,h) in items.items()}


def strict_interval(items,baseline):
    top,bottom=selected(scores(items,baseline))
    if len(top)!=2 or len(bottom)!=2:raise ValueError('Unique-cut method requires two selected members per side')
    constraints=[];lo=Q(0);hi=None
    for chosen,side in [(top,'top'),(bottom,'bottom')]:
        for i in chosen:
            for j in sorted(set(items)-set(chosen)):
                winner,loser=(i,j) if side=='top' else (j,i)
                w=items[winner][0]-items[loser][0];h=items[winner][1]-items[loser][1]
                if w-baseline*h<=0:raise ValueError('Baseline is not strictly separated')
                root=w/h if h else None
                if h>0:hi=root if hi is None or root<hi else hi
                elif h<0:lo=max(lo,root)
                elif w<=0:raise ValueError('Empty constant constraint')
                constraints.append({'side':side,'winner':winner,'loser':loser,'delta_W':w,'delta_H':h,'root':root})
    assert lo<baseline and (hi is None or baseline<hi)
    return lo,hi,(top,bottom),constraints


def synthetic_checks():
    # These exact examples exercise implementation; the report gives the proof.
    x={'A':(Q(12),Q(1)),'B':(Q(11),Q(-1)),'C':(Q(0),Q(0)),'D':(Q(-1),Q(0))}
    lo,hi,target,_=strict_interval(x,Q(1,4));assert (lo,hi)==(0,12)
    assert selected(scores(x,Q(1,2)))==target and selected(scores(x,Q(3,4)))==target
    assert weak_order(scores(x,Q(1,4)))!=weak_order(scores(x,Q(3,4)))
    parallel={'A':(Q(10),Q(2)),'B':(Q(10),Q(2)),'C':(Q(0),Q(2)),'D':(Q(-1),Q(2))}
    assert strict_interval(parallel,Q(1))[:2]==(0,None)
    boundary={'A':(Q(10),Q(1)),'B':(Q(9),Q(0)),'C':(Q(8),Q(-1)),'D':(Q(0),Q(0))}
    assert strict_interval(boundary,Q(1,2))[:2]==(0,1)
    assert strict_interval(boundary,Q(2))[:2]==(1,None)
    try:strict_interval(boundary,Q(1))
    except ValueError:pass
    else:raise AssertionError('Nonpersistent boundary tie must not enter unique-cut solver')
    permanent={'A':(Q(10),Q(0)),'B':(Q(9),Q(0)),'C':(Q(9),Q(0)),'D':(Q(0),Q(0))}
    assert len(selected(scores(permanent,Q(1)))[0])==3
    assert all(h==0 for w,h in permanent.values())  # symbolically constant ordering for all a
    try:strict_interval(permanent,Q(1))
    except ValueError:pass
    else:raise AssertionError('Persistent >2 cut requires general tie-aware algorithm')
    return ['internal_swap_does_not_shrink_interval','parallel_and_identical_selected_lines',
            'finite_excluded_boundary','positive_lower_bound_unbounded_right',
            'nonpersistent_cut_tie_rejected_by_unique_method','permanent_multi_member_cut_not_misclassified']


def run(owner,summary,out):
    assert sha(owner/'R005-ranking-sensitivity.md')=='984f4d57a29750028eeff4448892b3aa18293386fd9eb954194b70bafd5e9cc6'
    assert sha(owner/'R005-protocol.md')=='04db606fccb9b318414f5a0967f11666137fa180a3fc90414344c1a458a57c8e'
    assert sha(summary)=='8d359f9c86b544aaa6c573618a375eef7beb8f02070dc223f2802ce3fe31864d'
    validation_path=owner/'R005-validation.json';validation=json.loads(validation_path.read_text(encoding='utf-8'))
    files=[validation_path,summary]
    for item in validation['files']:
        p=owner/item['path'];assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes'];files.append(p)
    report=summary.parent/'report.md';assert sha(report)==validation['source_report_sha256'];files.append(report)
    snapshots=[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
    synthetic=synthetic_checks()
    source=readcsv(summary);assert len(source)==192
    groups=defaultdict(dict);max_reconstruction=Q(0)
    for row in source:
        key=(row['Case'],row['Story']);name=row['Link'];assert name not in groups[key]
        W=Q(row['Wtrap_native_kNm']);U=Q(row['DeltaUs_conditional_kNm']);H=U/AHAT
        groups[key][name]={'W':W,'H':H,'P':Q(row['max_abs_native_P_kN']),'native_D':Q(row['Dport_conditional_kNm'])}
        max_reconstruction=max(max_reconstruction,abs(W-U-Q(row['Dport_conditional_kNm'])))
    assert len(groups)==24 and all(len(x)==8 for x in groups.values())
    work=owner/'R005-affine-rank-results'
    intervals={(x['Case'],x['Story']):x for x in readcsv(work/'intervals.csv')};assert len(intervals)==24
    events={(x['Case'],x['Story'],x['side']):x for x in readcsv(work/'endpoint_events.csv')};assert len(events)==48
    pairrefs={(x['Case'],x['Story'],x['Link_i'],x['Link_j']):x for x in readcsv(work/'pair_crossings.csv')};assert len(pairrefs)==672
    author_cross=json.loads((work/'independent_crosscheck_complete.json').read_text(encoding='utf-8'))
    roots_count=Counter();results=[];mismatches=[];order_same=0
    for key,g in sorted(groups.items()):
        case,story=key;items={name:(x['W'],x['H']) for name,x in g.items()}
        lo,hi,(top,bottom),constraints=strict_interval(items,AHAT)
        assert len(constraints)==24
        row=intervals[key];assert row['status']=='maximal_open_interval' and row['baseline_rank_gate']=='True'
        assert (lo,hi)==(Q(row['a_lower_exact']),Q(row['a_upper_exact']))
        assert top==tuple(row['top_hat'].split(';')) and bottom==tuple(row['bottom_hat'].split(';'))
        assert selected({n:x['native_D'] for n,x in g.items()})==(top,bottom)
        Wset=selected(scores(items,Q(0)));assert Wset==(top,bottom)
        assert Wset[0]==tuple(row['top_W'].split(';')) and Wset[1]==tuple(row['bottom_W'].split(';'))
        order0=weak_order(scores(items,Q(0)));orderhat=weak_order(scores(items,AHAT));assert order0==orderhat;order_same+=1
        c=next(x for x in author_cross['groups'] if (x['Case'],x['Story'])==key)
        assert order0==c['W_full_weak_order'] and orderhat==c['hat_full_weak_order']
        peak=selected({n:x['P'] for n,x in g.items()})[0];assert peak==tuple(row['peak_force_top'].split(';'))
        if peak!=top:mismatches.append({'Case':case,'Story':story,'peak_top':list(peak),'W_and_hat_top':list(top)})
        assert (peak!=top)==(row['peak_top_differs_W']=='True')==(row['peak_top_differs_hat']=='True')
        positive=set();endpoint_ties={}
        for i,j in itertools.combinations(sorted(items),2):
            dw=items[i][0]-items[j][0];dh=items[i][1]-items[j][1]
            root=dw/dh if dh else None
            kind=('positive_root' if root>0 else 'zero_root' if root==0 else 'negative_root') if dh else ('identical_all_a' if dw==0 else 'parallel_no_root')
            roots_count[kind]+=1;pr=pairrefs[(case,story,i,j)]
            assert Q(pr['delta_W_exact'])==dw and Q(pr['delta_H_exact'])==dh and pr['intersection_kind']==kind
            assert (Q(pr['a_cross_exact']) if pr['a_cross_exact'] else None)==root
            if root is not None and root>0:positive.add(root)
        assert len(positive)==int(row['positive_distinct_roots'])
        for side,a in [('lower',lo),('upper',hi)]:
            values=scores(items,a);pattern=selected(values)
            ties=[[i,j] for i,j in itertools.combinations(sorted(items),2) if values[i]==values[j]]
            ep=events[(case,story,side)];assert Q(ep['a_endpoint_exact'])==a
            assert tuple(ep['top_endpoint'].split(';'))==pattern[0] and tuple(ep['bottom_endpoint'].split(';'))==pattern[1]
            assert json.loads(ep['tied_pairs_json'])==ties
            assert (ep['sets_same_as_hat']=='True')==(pattern==(top,bottom))
            if side=='upper':assert pattern!=(top,bottom)
            endpoint_ties[side]={'top':list(pattern[0]),'bottom':list(pattern[1]),'pairs':ties,'sets_same_as_hat':pattern==(top,bottom)}
        # All cross-member inequalities are strict throughout the intersection;
        # each active finite bound gives equality and extra boundary membership.
        active=[{'side':x['side'],'winner':x['winner'],'loser':x['loser']} for x in constraints if x['delta_H']>0 and x['root']==hi]
        assert active
        results.append({'Case':case,'Story':story,'lower_exact':str(lo),'upper_exact':str(hi),'upper_decimal':format(float(hi),'.17g'),
            'k_lower_exact':str(1/hi),'k_lower_decimal':format(float(1/hi),'.17g'),'strict_constraints':len(constraints),
            'top_hat':list(top),'bottom_hat':list(bottom),'full_W_weak_order':order0,'full_hat_weak_order':orderhat,
            'active_upper_constraints':active,'endpoint_events':endpoint_ties})
    assert roots_count==Counter({'positive_root':506,'negative_root':166})
    assert len(mismatches)==5 and order_same==24 and all(Q(x['lower_exact'])==0 for x in results)
    global_upper=min(Q(x['upper_exact']) for x in results)
    assert global_upper==Q('109364269142319412472415054009/4862139290568601250000000000000000')
    assert format(float(global_upper),'.17g')=='2.2493034980396427e-05'
    limiting=[x for x in results if Q(x['upper_exact'])==global_upper];assert len(limiting)==1
    limit=limiting[0];assert (limit['Case'],limit['Story'])==('SHW4Y','Story9')
    assert limit['endpoint_events']['upper']['pairs']==[['K66','K91']]
    assert set(limit['endpoint_events']['upper']['bottom'])=={'K8','K91','K66'}
    assert float(1/global_upper)>44458 and format(float(1/global_upper),'.12g')=='44458.2067681'
    assert global_upper==Q(validation['common_upper_a_exact'])
    text=(owner/'R005-ranking-sensitivity.md').read_text(encoding='utf-8')
    bound_rows=[];mismatch_rows=[]
    for line in text.splitlines():
        if line.startswith('| '):
            cells=[x.strip() for x in line.strip('|').split('|')]
            if len(cells)==4 and (cells[0],cells[1]) in groups:
                (bound_rows if cells[3].startswith('[[') else mismatch_rows).append(cells)
    assert len(bound_rows)==24 and len(mismatch_rows)==5
    for row in bound_rows:
        x=next(x for x in results if (x['Case'],x['Story'])==tuple(row[:2]))
        assert row[2]==format(float(Q(x['upper_exact'])),'.9g') and json.loads(row[3])==x['endpoint_events']['upper']['pairs']
    for row in mismatch_rows:
        x=next(x for x in mismatches if (x['Case'],x['Story'])==tuple(row[:2]))
        assert set(row[2].split('\u3001'))==set(x['peak_top']) and set(row[3].split('\u3001'))==set(x['W_and_hat_top'])
    for x in snapshots:
        p=Path(x['path']);assert sha(p)==x['sha256'] and p.stat().st_size==x['bytes']
    result={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,'script_sha256':sha(Path(__file__)),
        'method':'Independent Decimal-string Fraction coefficients and strict cross-member half-line intersection; no author code invocation/root-cell solver/grid approximation.',
        'a_hat_exact':str(AHAT),'H_definition':'stored DeltaUs divided by exact reported a_hat; no endpoint-force reconstruction',
        'groups_checked':24,'source_summary_rows':192,'strict_inequalities_checked':576,'pair_records_checked':672,'endpoint_events_checked':48,
        'pair_classification':dict(roots_count),'global_lower_exact':'0','global_upper_exact':str(global_upper),
        'global_upper_decimal':format(float(global_upper),'.17g'),'global_k_lower_exact':str(1/global_upper),
        'global_k_lower_decimal':format(float(1/global_upper),'.17g'),'limiting_case_story':['SHW4Y','Story9'],
        'all_full_W_vs_hat_weak_orders_equal_count':order_same,'peak_top_mismatch_groups':mismatches,
        'maximum_decimal_Dport_reconstruction_error_exact':str(max_reconstruction),
        'maximum_decimal_Dport_reconstruction_error_kNm':float(max_reconstruction),'synthetic_implementation_checks':synthetic,
        'proof_scope':'Cross-member strict inequalities are necessary and sufficient only for actual unique-cut sets of size two. General degenerate cases audited via pairwise sign-cell theorem in report, not inferred from finite tests.',
        'records':results,'inputs_before_and_after':snapshots,
        'limits':['Exact statements concern frozen decimal summary coefficients only, not continuous physical values or independent force/port certification.',
                  'a/k intervals are not confidence/identification/positive-dissipation domains or guarantees for true changed-k trajectories.',
                  'Upstream R011 is an arithmetic review, not physical/novelty certification; source candidate labels preserved.',
                  'No NPZ/Excel/full histories, author-script calls, model changes, full-array outputs or uploads.']}
    out.mkdir(parents=True,exist_ok=True);target=out/'review_summary.json';assert not target.exists()
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ['recorded_at','checks_passed','groups_checked','strict_inequalities_checked','pair_records_checked',
        'global_upper_exact','global_upper_decimal','global_k_lower_decimal','all_full_W_vs_hat_weak_orders_equal_count',
        'maximum_decimal_Dport_reconstruction_error_kNm','pair_classification','peak_top_mismatch_groups']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--owner',required=True,type=Path);parser.add_argument('--summary',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();run(args.owner,args.summary,args.out)
