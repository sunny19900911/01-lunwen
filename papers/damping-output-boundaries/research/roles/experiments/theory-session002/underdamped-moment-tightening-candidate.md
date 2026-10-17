# 欠阻尼紧域的一阶核矩改进候选

E-EXP-T002-004，`analytic-derivation / arithmetic-check / candidate`，待不同作者审核。**给定替代式成立，但只限整个共同阻尼区间严格欠阻尼。unit本例可将矩与相应充分时长常数缩至原约0.121889倍，约改善8.204倍。** 这是保守证书的改进，不是必要时长、实际峰值或工程可行性结论；E3冻结记录不改。

## 1. 独立核对包络与积分

假设对两个状态及整个r邻域，都有`0<zeta_minus<=zeta<=zeta_plus<1`。对任意omega>0、t>=0，欠阻尼单位模态核为

`g_zeta,omega(t)=exp(-zeta*omega*t)*sin(omega*sqrt(1-zeta²)*t)/(omega*sqrt(1-zeta²))`。

利用`abs(sin)<=1`、`zeta>=zeta_minus`及`1/sqrt(1-zeta²)<=1/sqrt(1-zeta_plus²)`，逐点得到

`abs(g_zeta,omega(t)) <= exp(-zeta_minus*omega*t)/(omega*sqrt(1-zeta_plus²))`。

对固定真实topcut核`h_zeta=sum rho_i*g_zeta,omega_i`，先三角不等式，再用`integral_0^infty t*exp(-a*t)dt=1/a²`，有

`m_zeta=integral_0^infty t*abs(h_zeta(t))dt <= sum_i abs(rho_i)/(zeta_minus²*omega_i³*sqrt(1-zeta_plus²)) = M_alt`。

因此该式系数与omega三次幂正确，对整个阻尼紧区间统一。它没有使用输出模态抵消，仍是保守上界。若zeta_plus>=1，分母不再提供这个有效的有限欠阻尼包络，不能沿用；临界及过阻尼仍按C023原统一界处理。

## 2. 为什么取min

两套上界都有效时，当然有`m_zeta<=M_best=min(M_old,M_alt)`。原统一式在本欠阻尼紧区间有gamma=zeta_minus，故若记`S_rho=sum abs(rho_i)/omega_i³>0`，

`M_old=2*zeta_minus^(-3)*S_rho`，且

`M_alt/M_old = zeta_minus/(2*sqrt(1-zeta_plus²))`。

替代式较小时才改善；它不是所有欠阻尼区间上的一致支配。例如zeta_plus趋1而zeta_minus保持正时，这个比值可增大。因此通用实现应先判断适用域，再取两套有效界的min，不能无条件替换原界。本轮只评价既有unit紧域，不增加其他参数或反例数值。

## 3. 固定unit的普通近似

直接复用E1冻结omega/rho及E3常数，zeta_minus≈.211783418330635、zeta_plus≈.495247378250101，严格欠阻尼条件有充分数值余量；`sqrt(1-zeta_plus²)≈.868751998176926`。本源含完整rho，无新谱或补留数。

| 证书常数 | E3原值近似 | 替代值近似 |
|---|---:|---:|
| M | 631.648383249 | 76.991278333 |
| E=pi M/2 | 992.190960233 | 120.937617200 |
| T0=2E/B，半时长/s | 4369372.347956 | 532580.422118 |
| Tenv=E/A，时间/s | 519981.424358 | 63380.253369 |

新/旧比均为`0.121889456815675`，保留约12.18895%；旧/新约`8.20415502805`。本例M_alt<M_old，所以M_best=M_alt。T0替代值约6.16413天、Tenv约.733568天，均为原unit模型一致时间，不据此称工程可行。

A、B、eta及`C=B/(2A)`不变；只改变核矩引入的E和线性依赖E的充分时长。旧四delta的Tenv/delta若按同一替代证书更新，也同比缩放；按要求本轮没有创建新delta表或图，也没有计算任何时长的响应。并未证明该替代矩、时间或完整峰比最优。

## 4. 真实执行与来源

2026-10-17 12:56:35读取输入；实际执行标准库脚本[underdamped-moment-tightening-calc.py](underdamped-moment-tightening-calc.py)，Python3.12.14、Decimal90位普通就近舍入，退出0，8项检查通过，约0.00103 s。输出[underdamped-moment-tightening-values.json](underdamped-moment-tightening-values.json)记录真实完成时刻、argv、代码SHA、完整常数与比值、依赖、退出及检查；这不是定向舍入区间认证，也不重新认证原冻结谱的误差。

绑定并在运行后核对未变的源SHA256：

- E1 `detuning_values.json`：`7df5437996e7cf9a2f42d4dfc244ed481c96051236d1453861b03ae8ffeb9907`。
- E3 `envelope_constants.json`：`4da924405d0766f6108d53d67e42caa692b98230ea59516b1b94fc9f1ae7ac9b`。
- C023候选原文：`ea99a02b167720490242edc396adc6da154dd617a55dfc8df26c28c2daf3b3db`。

未新算响应、根、r、谱、模型、拟合或图，未覆E3。解析式与数值先candidate，交不同作者独审后由主控裁决；不自行入稿或升格共享主张。新会话截止14:19:08不变。
