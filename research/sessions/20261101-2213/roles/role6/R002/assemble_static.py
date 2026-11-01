"""Static reconstruction only. No record reading or dynamic integration."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "roles/role3/R002/assembly-inputs.json"
SETTINGS = ROOT / "public-benchmark-settings-freeze-v001.json"
TZ = timezone(timedelta(hours=8))


def rel(a, b):
    return float(np.linalg.norm(a-b) / max(np.linalg.norm(b), 1e-30))


def elastic_element(E, A, I, xi, xj):
    dx, dy = np.asarray(xj)-np.asarray(xi)
    length = float(np.hypot(dx, dy))
    c, s = dx/length, dy/length
    rot = np.array([[c,s,0],[-s,c,0],[0,0,1.]])
    transform = np.zeros((6,6))
    transform[:3,:3] = transform[3:,3:] = rot
    axial, b, d, e, f = E*A/length, 12*E*I/length**3, 6*E*I/length**2, 4*E*I/length, 2*E*I/length
    local = np.array([
        [axial,0,0,-axial,0,0],
        [0,b,d,0,-b,d],
        [0,d,e,0,-d,f],
        [-axial,0,0,axial,0,0],
        [0,-b,-d,0,b,-d],
        [0,d,f,0,-d,e]])
    rigid = np.array([[1,0,0,1,0,0],[0,1,0,0,1,0],[0,0,1,0,length,1.]]).T
    rigid_residual = float(np.linalg.norm(local@rigid)/(np.linalg.norm(local)*np.linalg.norm(rigid)))
    return transform.T@local@transform, local, transform, rigid_residual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True, help="new output directory; refuses overwrite")
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=False)
    local = out/"local-cache"
    local.mkdir()
    start = datetime.now(TZ)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "1fa391c0fc059463475a529db82a890dcfb1f104400cc4d77247341b5504104e"
    nodes = source["nodes"]
    tags = [n["tag"] for n in nodes]
    index = {tag:i for i, tag in enumerate(tags)}
    coords = {n["tag"]:[n["x_in"],n["y_in"]] for n in nodes}
    labels = [f"{tag}.{d}" for tag in tags for d in ("ux","uy","rz")]
    K = np.zeros((48,48))
    M = np.zeros((48,48))
    cut = np.zeros((3,48))
    rigid_errors = []
    element_maps = []
    for item in source["elements"]:
        i,j = item["i"],item["j"]
        sec = source["sections"][item["section"]]
        kg, kl, transform, rigid_error = elastic_element(source["E_kip_per_in2"], sec["A_in2"], sec["Iz_in4"], coords[i],coords[j])
        dofs = np.r_[np.arange(3*index[i],3*index[i]+3),np.arange(3*index[j],3*index[j]+3)]
        K[np.ix_(dofs,dofs)] += kg
        rigid_errors.append(rigid_error)
        if item["section"] == "column":
            story = int(coords[j][1]/168)-1
            # Positive elastic resisting force exerted at upper (j) end, global +x.
            cut[story,dofs] += kg[3,:]
            element_maps.append({"element":item["tag"],"story":story+1,"node_i":i,"node_j":j,"end":"j","component":"global_x","sign":1})
    for item in source["nodal_masses"]:
        M[3*index[item["node"]],3*index[item["node"]]] = item["mx_kip_s2_per_in"]
    fixed = sorted(3*index[s["node"]]+k for s in source["supports"] for k,flag in enumerate(s["fixed_dofs"]) if flag)
    free = np.array([i for i in range(48) if i not in fixed])
    massive = np.array([i for i in free if M[i,i]>0])
    massless = np.array([i for i in free if M[i,i]==0])
    assert (len(nodes),len(source["elements"]),len(fixed),len(free),len(massive),len(massless)) == (16,21,8,40,12,28)
    Kzz = K[np.ix_(massless,massless)]
    eigenzz = np.linalg.eigvalsh(Kzz)
    diagonal_scale = 1/np.sqrt(np.diag(Kzz))
    scaledzz = diagonal_scale[:,None]*Kzz*diagonal_scale[None,:]
    assert np.linalg.matrix_rank(scaledzz)==28
    assert np.linalg.eigvalsh(scaledzz)[0]>0
    H = np.zeros((48,12))
    H[massive,:] = np.eye(12)
    H[massless,:] = -np.linalg.solve(Kzz,K[np.ix_(massless,massive)])
    Kraw = K[np.ix_(massive,massive)] + K[np.ix_(massive,massless)]@H[massless,:]
    asym = rel(Kraw,Kraw.T)
    assert asym<1e-11
    Kc = (Kraw+Kraw.T)/2
    Mc = M[np.ix_(massive,massive)]
    invroot = 1/np.sqrt(np.diag(Mc))
    eig, vectors = np.linalg.eigh(invroot[:,None]*Kc*invroot[None,:])
    assert eig[0]>0
    phi = invroot[:,None]*vectors
    for r in range(12):
        if phi[np.argmax(np.abs(phi[:,r])),r]<0:
            phi[:,r] *= -1
    omega = np.sqrt(eig)
    fullphi = H@phi
    influence = np.ones(12)
    gamma = phi.T@Mc@influence
    selector = np.array([[float(coords[tags[d//3]][1]>=h) for d in massive] for h in (168,336,504)])
    full_selector = np.zeros((3,48))
    full_selector[:,massive] = selector
    L = selector@Mc@phi
    B = L*gamma[None,:]
    C = cut@H
    Cmodal = C@phi
    modal_mass = np.diag(phi.T@Mc@phi)
    factors = np.array([-.3,1.7,-2.1,.6,-1.2,2.5,-.8,1.1,-3.2,.4,-1.6,2.3])
    changedphi = phi*factors[None,:]
    changedmass = np.diag(changedphi.T@Mc@changedphi)
    changedgamma = (changedphi.T@Mc@influence)/changedmass
    changedB = (selector@Mc@changedphi)*changedgamma[None,:]
    condensed_eigen = Kc@phi-Mc@phi*eig[None,:]
    full_eigen = K@fullphi-M@fullphi*eig[None,:]
    checks = {
        "full_dimension":48,"free_dimension":40,"massive_dimension":12,"massless_dimension":28,
        "Kzz_rank":int(np.linalg.matrix_rank(scaledzz)),
        "Kzz_min_eigenvalue_mixed_dof_units":float(eigenzz[0]),
        "Kzz_condition2_mixed_dof_units":float(np.linalg.cond(Kzz)),
        "Kzz_diagonally_scaled_min_eigenvalue":float(np.linalg.eigvalsh(scaledzz)[0]),
        "Kzz_diagonally_scaled_condition2":float(np.linalg.cond(scaledzz)),
        "K40_min_eigenvalue_mixed_dof_units":float(np.linalg.eigvalsh(K[np.ix_(free,free)])[0]),
        "K12_min_eigenvalue_kip_per_in":float(np.linalg.eigvalsh(Kc)[0]),
        "full_symmetry_relative":rel(K,K.T),"condensed_raw_symmetry_relative":asym,
        "maximum_element_rigid_motion_relative_residual":max(rigid_errors),
        "condensed_energy_matrix_relative":rel(H.T@K@H,Kc),
        "mass_restoration_relative":rel(H.T@M@H,Mc),
        "massless_equilibrium_relative":float(np.linalg.norm((K@H)[massless,:])/np.linalg.norm(K@H)),
        "condensed_eigen_relative":float(np.linalg.norm(condensed_eigen)/np.linalg.norm(Mc@phi*eig[None,:])),
        "full_free_eigen_relative":float(np.linalg.norm(full_eigen[free,:])/np.linalg.norm((M@fullphi*eig[None,:])[free,:])),
        "modal_mass_orthogonality_relative":rel(phi.T@Mc@phi,np.eye(12)),
        "massive_shape_recovery_relative":rel(fullphi[massive,:],phi),
        "cut_vs_upper_domain_K_relative":rel(cut,full_selector@K),
        "cut_vs_inertia_modal_relative":rel(Cmodal,L*eig[None,:]),
        "sign_and_scale_B_invariance_relative":rel(changedB,B),
        "effective_mass_sum":float(np.sum(modal_mass*gamma**2)),
        "total_mass":float(influence@Mc@influence),
        "effective_mass_closure_relative":float(abs(np.sum(modal_mass*gamma**2)-influence@Mc@influence)/(influence@Mc@influence)),
        "floor_mass_above":(selector@Mc@influence).tolist(),
        "sum_B_per_cut":np.sum(B,axis=1).tolist(),
        "B_mass_closure_relative":rel(np.sum(B,axis=1),selector@Mc@influence),
    }
    tolerance_keys = [k for k in checks if k.endswith("_relative") or k.endswith("_residual")]
    assert all(checks[k]<1e-10 for k in tolerance_keys), checks
    assert checks["K40_min_eigenvalue_mixed_dof_units"]>0
    metadata = {
        "identity":settings["identity"],"units":{"displacement":"in","force":"kip","time":"s","mass":"kip*s2/in","omega":"rad/s","B":"kip*s2/in"},
        "source_assembly_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "settings_sha256":hashlib.sha256(SETTINGS.read_bytes()).hexdigest(),
        "dof_order":[labels[i] for i in massive],
        "matrix_rows_and_columns":"M12/K12/Phi12 follow dof_order; Phi12 columns are modes 1..12",
        "normalization":"phi^T M phi=I; largest-absolute horizontal component of each mode positive",
        "massless_recovery":"u48=H48x12*u12; constrained DOFs zero, 28 massless DOFs H_z=-solve(Kzz,Kzx); H local cache or reconstruct from script",
        "elastic_cut_convention":"V_s=sum(global +x resisting force at upper j ends of four columns crossing story bottom); C3x12 maps u12 to V in kip",
        "modal_equations":"q_r''+2*zeta*omega_r*q_r'+omega_r^2*q_r=-Gamma_r*ag; q=Gamma*s; V_s=sum(B_sr*omega_r^2*s_r)",
        "L_definition":"L_sr=r_s^T M phi_r; B_sr=Gamma_r*L_sr, not Gamma times Cmodal",
        "source_story_node_prefix":[2,3,4],"physical_story_order":[1,2,3],
        "no_floor_merging":True,"no_added_mass":True,"no_dynamic_response_generated":True,
        "software_scope":"Self-written linear Euler-Bernoulli frame reconstruction of source elastic-section/Linear-geometry parameters; OpenSees not invoked or solver-equivalence validated.",
        "M12":Mc.tolist(),"K12":Kc.tolist(),"Phi12":phi.tolist(),
        "omega12":omega.tolist(),"period12":(2*np.pi/omega).tolist(),"Gamma12":gamma.tolist(),
        "modal_mass12":modal_mass.tolist(),"effective_mass12":(modal_mass*gamma**2).tolist(),
        "L3x12":L.tolist(),"B3x12":B.tolist(),"C3x12":C.tolist(),"Cmodal3x12":Cmodal.tolist(),
        "story_mass_selector3x12":selector.tolist(),"cut_members":element_maps,
    }
    for name,data in [("static-interface.json",metadata),("static-checks.json",checks)]:
        with (out/name).open("x",encoding="utf-8",newline="\n") as f:
            json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.write("\n")
    # Only small derived interface is proposed for Git. Full reconstruction matrices stay local.
    np.savez(local/"static-full-recovery.npz",K48=K,M48=M,H48x12=H,Phi48x12=fullphi,Kzz=Kzz,cut3x48=cut,free=free,massive=massive,massless=massless)
    report=f"""# 公开三层框架：静态组装与模态输出接口

已按16节点、21梁柱原拓扑组装48自由度弹性刚度，约束8个柱脚平动后保留40自由度。28个零质量自由度的Kzz满秩且正定，凝聚为12个独立水平质量自由度；未添加小质量，未合并同层节点。

主要结果：总水平质量{checks['total_mass']:.12g} kip·s²/in；第一周期{2*np.pi/omega[0]:.9g} s；12阶频率全部为正。Kzz经对角尺度变换后最小特征值{checks['Kzz_diagonally_scaled_min_eigenvalue']:.6g}，条件数{checks['Kzz_diagonally_scaled_condition2']:.6g}。尺度变换只用于数值检查，未改变凝聚模型。

静态接口见static-interface.json：M12、K12、质量归一振型、12阶ω/Γ、三层L/B、位移到弹性层剪力C，以及逐层跨越柱名单。自由度顺序是21..24、31..34、41..44各节点ux。输入使用in、kip、s；B单位kip·s²/in。三层指物理第1/2/3层，对应原节点层号2/3/4。

层剪力采用每层底面四根跨越柱的上端全局+x弹性恢复力之和。若u12=Phi*q，则V=C*Phi*q；单位核s满足s''+2ζωs'+ω²s=−ag，q=Γs，因此V_s=ΣB_sr ω_r² s_r，B=Γ(r_sᵀMφ_r)。不可再乘一次Γ，不把阻尼支座反力作为弹性剪力。

实际检查：凝聚特征方程相对残差{checks['condensed_eigen_relative']:.3g}；恢复到40个自由度后的Kφ=ω²Mφ残差{checks['full_free_eigen_relative']:.3g}；柱端剪力映射与ω²L相对差{checks['cut_vs_inertia_modal_relative']:.3g}；反号及缩放后B相对差{checks['sign_and_scale_B_invariance_relative']:.3g}；完整12阶基底有效质量闭合相对差{checks['effective_mass_closure_relative']:.3g}。全部静态相对检查低于1e−10，详见static-checks.json，独立审核待②完成。

柱脚rz保持自由，uy和rz的质量保持零；H恢复全部节点位移和转角。完整48阶矩阵与H仅保存在local-cache/static-full-recovery.npz；可从自写脚本复组装。只有小矩阵接口、参数说明、检查和自写脚本可供主控核后Git。

本项为OpenSees官方Example5弹性截面、Linear几何参数的自写线性重构。源单元为nonlinearBeamColumn、5积分点，本项未运行OpenSees，也不声称与其软件结果已作等价验证。官方出处与原文件散列见③R002的public-multistory-benchmark.md/source-manifest.json；原Tcl/AT2未复制至本接口，未读取地震记录、未计算地震响应、灵敏度或候选真值。

④下一步可直接读取static-interface.json，在根冻结的输入/阻尼/时间窗下生产动态预测；新目标参考响应仍须在预测冻结后产生。②可运行本脚本至新的隔离目录检查复现；原冻结输出拒绝覆盖。
"""
    with (out/"one-page.md").open("x",encoding="utf-8",newline="\n") as f:
        f.write(report)
    result = {"actual_script_start":start.isoformat(),"actual_script_end":datetime.now(TZ).isoformat(),"checks":checks,"first_period":float(2*np.pi/omega[0]),"omega12":omega.tolist(),"files_produced":[x.name for x in out.iterdir() if x.is_file()]}
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))


if __name__=="__main__":
    main()
