# round-001来源散列差异的可复核说明

2026-10-17 09:13 +08:00。回应作者QW06及验证者对V002来源指纹的质询。原round-001.md保持冻结，不为统一散列改写证据文件。

初次落盘时首段写“记录冻结2026-10-17 09:00 +08:00”。本角色随后读取真实时钟08:59:22，发现该分钟标记比实际时间早写到下一分钟，因而在正式宣布冻结前只将该字串改为“记录冻结2026-10-17 08:59 +08:00”，之后交付主控和验证角色。数学内容没有因该修改变化。

2026-10-17 09:13:08 +08:00，实际只读复核确认：

- 当前原文件字节SHA256：`c27ba79e4330f4a717c434188222a5f0ea7d0187cc374f5fa9e7dc5025f52671`，不含CRLF。
- 将当前文本中上述唯一时间字串反向替换为09:00，不写文件，计算所得SHA256：`affe7a13dbfa0465af8239de0af0c770b15e3bdf1c7e6b322d758c1f1c8671c7`，与验证者早期记录完全一致。
- 若再改为CRLF则所得为另一个散列，故本次差异已由时间字串修正精确解释，不需要假定换行或编码变化。

复现（仓库根目录，标准库Python；只读）：

```python
from pathlib import Path
import hashlib
p=Path('papers/damping-output-boundaries/research/roles/ideation/round-001.md')
b=p.read_bytes()
print(hashlib.sha256(b).hexdigest())
s=b.decode('utf-8')
before='记录冻结2026-10-17 08:59 +08:00'
after='记录冻结2026-10-17 09:00 +08:00'
assert s.count(before)==1
print(hashlib.sha256(s.replace(before,after).encode('utf-8')).hexdigest())
```

旧字节文件未另行归档；以上是从当前内容按已执行单次修改重构并与已存早期散列精确匹配。此说明不把两个观察时点写成同一输入版本。后续引用以当前冻结c27ba79e…为准，早期审核记录保留原散列并链接本说明。
