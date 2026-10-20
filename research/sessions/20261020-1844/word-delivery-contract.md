# 最后45分钟交付要求

固定截止21:44:25，不从成稿/唤醒重算。20:59:25起由唯一作者角色5制作最终Word；输入必须是主控已经阅读全文、科学/措辞/引用审查完成、明确冻结及SHA的canonical版本，不自行取目录中最大的版本号或在写稿。

正文保持结构工程常用语言；内部记录、SHA、工具失败与角色任务不放入Word论文。模型假定、真实工程剪力与已知三层弹性剪力的区别、输入/初始条件、装置力正方向及实际对照范围用必要短段保留。作者信息留待作者填写，不编人名单位。

使用documents与engineering-paper-writing技能，复用已有Word构建工具但不能保留旧稿固定8公式等断言。主文/表格可编辑；显示公式、M/K矩阵宜用可编辑Word数学结构或清晰原生格式，不漏出LaTeX命令/程序数组。图用role4R008批准中文PNG与相应图注，原几何不变。最多3主图，确保缩放后轴、标注可读。

捆绑Python：C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe；python-docx/PIL/reportlab可用，matplotlib/cairosvg/svglib已知不可用，不安装。Node的sharp绝对入口在同依赖目录node/node_modules/sharp/dist/index.cjs；图已渲染，不需再重作。现有research/exports/20261018-word-v019/render_word_native.ps1可读后按需复用，注意新COM实例隐藏且只关闭本任务文档，不能关闭用户其他文档。若使用LibreOffice，只用load_workspace_dependencies所给依赖包内路径，不用用户桌面LibreOffice。

生成新文件modal-shear-session009-论文审阅稿.docx，允许版本后缀；旧Word/旧稿原样保留。最终文档去除不必要作者元数据，不读账户信息。不要制作用户未要求的投稿或外发。

每次有版面实质变动后重新渲染；最终必须逐页实际PNG查看（不是抽页、不是只ZIP/XML检查）。检查数学符号、字体、图、宽表、分页、标题与图注关联；QA过程与逐页图留自己的local-cache或本地导出目录，Git仅明确的最终小Word/脚本/清单，不自动加入整页截图/大缓存。若渲染受阻如实说明，不认已通过。主控可另看全部页复核。

角色5完成后冻结源SHA、WordSHA、表图公式计数、渲染页数和实际查看范围。正常Git最后一次同步，主控写final-summary和普通中文结论，正式暂停automation-5并读回。截止后的操作仅必要收集/审核现成增量及行政收束，不延长科研。
