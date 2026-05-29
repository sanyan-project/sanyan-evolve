# Sanyan Evolve — 自进化AI Agent

> 用达尔文进化论驱动AI自我优化。给定任务，引擎自动进化出最优解。
> G11000+代云端验证 · Reasonix Skill + 独立Python包

## 5秒体验

```python
from evolve_agent import evolve
import numpy as np

target = [0.8, 0.3, 0.5, 0.9, 0.2, 0.7]
result = evolve("向目标收敛", lambda g: 1/(1+np.linalg.norm(g-target)), pop_size=30, generations=50)
# 50代后fitness 0.99+，误差<0.2%
```

## Reasonix Skill

在Reasonix中直接调用：
```
/skill sanyan-evolve "优化这个函数的参数"
```

## 安装

```bash
pip install numpy
git clone https://github.com/sanyan-project/sanyan-evolve
cd sanyan-evolve
python evolve_agent.py
```

## 关于

基于三衍进化引擎v43（11000+代云端验证）精简而来。
