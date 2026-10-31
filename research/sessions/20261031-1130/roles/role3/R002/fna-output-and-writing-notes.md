# FNA有效刚度、目标剪力与模态运动：原文补充及作者用段落

角色③续写；90分钟实际窗口11:41:38—13:11:38+08。本项只复用CSI/Song，补充R001之后发现的输出刚度条件，不改整稿。以下公式映射待验证角色独立复核，不预设实际模型的有效Link刚度非零。

## 原文依据与解释

CSI Analysis Reference Manual，July 2016 Rev.15，印刷452/PDF474，“Link/Support Effective Stiffness”及“Mode Superposition”：为非线性Link自由度设置线性有效刚度K_N，组合刚度为K=K_L+K_N。原文以K_L表示线性构件及Link线性自由度的刚度，以r_N表示非线性自由度力。方程写为

$$M\ddot u+C\dot u+Ku=r-[r_N-K_Nu].$$

印刷453/PDF475：采用该K和M构成模态，单位模态质量下有Ω²=ΦᵀKΦ、I=ΦᵀMΦ；广义非线性力为Φᵀ[r_N−K_Nu]。原文明确指出这一项通常使模态方程耦合。两页已渲染并逐页查看；仅本地缓存存原页图，不作为发布文件。

[CSI官方手册](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf)。原文文件指纹沿用R001并已核一致。

### 解释一：用于模态分析的K与目标力算子分别定义

若目标输出是K_L对应的线性部分，设其切口合力采用a_sᵀK_Lu，且e_r=Kφ_r−ω_r²Mφ_r，则对于同一坐标q_r，逐项代入得到

$$a_s^{\mathsf T}K_L\phi_rq_r
=\omega_r^2a_s^{\mathsf T}M\phi_rq_r
+a_s^{\mathsf T}e_rq_r
-a_s^{\mathsf T}K_N\phi_rq_r.$$

这里第一项是质量投影对应项，第二项为该K下的全空间特征残差项，第三项为有效刚度与目标线性输出之间的差项。即使采用该K的精确Eigen振型，第二项为零也不使第三项自动为零。只有目标算子、切口与K_L的这种表达确实成立时才使用此式；一般三维局部构件力应直接写目标恢复算子H_sφ_rq_r。

该式是对手册方程的解释性代数映射，不是手册给出的楼层公式。它不证明当前模型采用了何种K_N、不判断具体表中的Story Forces包含哪些力，也不将某个虚拟有效刚度解释为物理装置刚度。

### 解释二：模态基可用，不等于实际坐标已取得

位移可表示为u=Φq时，任何线性目标输出都可采用相应系数H_sΦ乘实际q。这个输出关系与q是否满足独立SDOF是不同问题。FNA中即使质量和线性刚度已对角化，右端非线性广义力仍依赖多阶坐标；仅有周期、阻尼比和输入不能自动重建实际FNA各阶时程。

Song等MCEER-08-0005，印刷38/PDF56式(3.58)–(3.59)给出剪切楼模型中弹性输出T_SKx与含阻尼输出T_S(Cẋ+Kx)的区别。把这个区别用于FNA时，还应明确所称K是否为目标线性部分、模态有效刚度，或另一个构件恢复算子；不能仅因都记为K而合并。

## 可供正文选用的中文段落

**模态分析与力恢复。** 对有限元模型进行模态分析时，应同时明确用于求取振型的刚度和目标剪力的组成。对于采用非线性Link的FNA分析，模态刚度可以包含非线性自由度的线性有效刚度，而实际非线性力通过广义力项参与动力平衡。因而，由频率和质量投影得到的项首先对应所采用的模态刚度。恢复主体线性构件的弹性剪力时，还应采用相应构件或切口的力恢复关系，并计入两者刚度定义的差别。

**实际模态运动。** 物理输出系数说明某阶坐标如何形成目标剪力，不能单独确定该阶在实际有控分析中的运动。FNA虽然采用实模态基进行计算，非线性Link力仍可使各阶方程相互耦合。本文因此分别核对模态输出关系和模态时程来源；独立单自由度方程得到的单位响应，仅用于符合其解耦假定的线性参照分析。

**工程含义。** 对比增阻尼方案时，应先确认两方案采用同一结构质量、相应刚度及输出定义，再比较各阶运动和带符号剪力项。若实际装置改变了参与模态分析的有效刚度，应重新核对模态基及目标恢复系数，不仅按阶号或接近的周期迁移原有系数。

## 英文方法段落（对应中文条件，供作者选用）

The stiffness matrix used to generate the modal basis and the operator used to recover the target story shear must be identified separately. In fast nonlinear analysis, the modal stiffness may include the linear effective stiffness assigned to nonlinear link degrees of freedom. The actual nonlinear forces enter the equations through an additional generalized force term. A coefficient obtained from modal frequency and mass projection therefore corresponds first to the stiffness adopted in the modal analysis. Recovering the elastic shear of the linear structural components additionally requires the appropriate force recovery operator and any correction caused by the difference between these stiffness definitions.

The physical output coefficients and the actual modal response histories are also distinct inputs. A real modal basis does not ensure independent single degree of freedom response in FNA, because the nonlinear generalized forces can couple the modal coordinates. Unit response histories calculated from uncoupled equations are used only for the corresponding linear reference model.

## 作者引用位置建议

- “FNA有效刚度及非线性补偿项”引用CSI印刷452/PDF474。
- “FNA广义力耦合及质量归一化”引用CSI印刷453/PDF475。
- “弹性/含阻尼剪力分开”引用Song印刷38/PDF56式(3.58)–(3.59)，并保留剪切楼对象条件。
- 本项输出算子差项为代数解释，送②独审；在独审前只作为应检查的模型条件，不宣布已修正当前工程系数。

未新增文献、数据读取、拟合、求解/API或Git操作。未进入⑤所有的正文目录。
