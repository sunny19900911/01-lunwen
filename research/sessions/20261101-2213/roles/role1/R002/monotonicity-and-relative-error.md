# 附注：误差界单调性、二分和目标峰相对误差

## 1．只证明误差界函数单调，不证明响应单调

在0<ζ<1，置 \(u=\zeta/\sqrt{1-\zeta^2}\)、\(\kappa=\coth(\pi u/2)\)。直接求导有
\[
\kappa'<0,\qquad
-\zeta\frac{\kappa'}{\kappa}
=\frac{\pi u(1+u^2)}{\sinh(\pi u)}\le1.
\]
末步因为 \(\sinh(\pi u)\ge\pi u+(\pi u)^3/6\ge\pi u(1+u^2)\)，其中 \(\pi^2\ge6\)。故对δ>0、ζ=ζ0+δ、n≥1，
\[
\frac{d}{d\delta}\log[\delta^n\kappa(\zeta_0+\delta)]
\ge\frac n\delta-\frac1{\zeta_0+\delta}>0.
\]
ζ≥1时κ=1，仍递增，且在ζ=1连续。因而一/二阶界对应n=2、3，在正侧均递增。负侧x=−δ>0时，x的幂增大且κ(ζ0−x)增大，也严格递增。这一结论不适用于真实P(ζ)、改善D(ζ)、控制峰时刻或剪力的单调性。

## 2．二分返回已通过端点

预先给工程允许上限d_cap和半径精度ηδ。正侧测试F(d)=J d^n κ(ζ0+d)，负侧测试F(d)=J d^n κ(ζ0−d)，后者须d_cap<ζ0。若F(d_cap)≤预算，返回d_cap，含义是“该上限内全部通过”，不是域外最大值。否则从lo=0、hi=d_cap开始：F(mid)≤预算时令lo=mid，否则hi=mid；hi−lo≤ηδ后返回lo，同时保存括区间及预算余量。若直接乘方或coth的数值溢出，视为该试点未获得界，不把非数当作通过；靠近ζ=1可用连续极限。

若有固定数值误差预留E_num，先从预算扣除；预算非正时不做半径认证。若E_num随δ变化，必须给出在搜索区间内统一上界或另证其单调，不能直接沿用上述二分保证。J=0须先判断是真正零尺度还是导出精度零；仅有显示零不授权无限半径。

## 3．误差以目标峰为分母时

预算ε0P0对应相对基准峰误差，不等于相对未知目标峰。若要求 \(|\hat P-P_*|/P_*\le\varepsilon_*\)，候选预测已给出 \(\hat P>E_{total}\) 时，充分条件是
\[
\frac{E_{total}}{\hat P-E_{total}}\le\varepsilon_*
\quad\Longleftrightarrow\quad
(1+\varepsilon_*)E_{total}\le\varepsilon_*\hat P.
\]
候选\(\hat P\)只由基准多项式整时程求峰，不是目标真值；但该候选条件未证明单调，不能凭其一次通过外推全部更小δ。

若希望仍用单调标量式求半径，基准再保存
\(G_1=\|\sum_rc_rz_r\|_\infty\)、\(G_2=\|\sum_rc_rw_r\|_\infty\)。记 \(M_1(x)=xG_1\)、\(M_2(x)=xG_1+x^2G_2/2\)，则 \(\hat P_p\ge P_0-M_p\)。因此以下是更保守的充分条件：
\[
(1+\varepsilon_*)E_{total,p}+\varepsilon_*M_p
\le\varepsilon_*P_0,
\qquad P_0-M_p-E_{total,p}>0.
\]
固定E_num时，左端在正/负增量绝对值上均不减，亦可二分。零目标峰的相对误差无定义，转为绝对力误差。此规则与改善目标、峰区状态分别报告；未通过界表示直接外推未获该误差预算支持，不等于目标方案本身不利。
