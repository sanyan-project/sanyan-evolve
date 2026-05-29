#!/usr/bin/env python3
"""
Sanyan Evolve — 自进化AI框架Agent核心

独立Python模块，可在Reasonix外使用。
也可被包装为Reasonix skill（/skill sanyan-evolve）
"""
import random
import numpy as np
import json
from typing import Callable, List, Optional

class EvolveAgent:
    """自进化Agent核心引擎"""
    
    def __init__(self, pop_size=30, generations=50, mutation_rate=0.15):
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.population = []
        self.history = {"bf": [], "diversity": [], "best_genome": None}
    
    def run(self, task: str, evaluator: Callable, genome_dim=6):
        """
        运行进化
        
        task: 任务描述
        evaluator: 评估函数，接收genome返回fitness
        genome_dim: 基因组维度
        """
        # 1. 初始化种群
        self.population = [
            np.random.uniform(0, 1, genome_dim) for _ in range(self.pop_size)
        ]
        
        for gen in range(self.generations):
            # 2. 评估
            scored = [(g, evaluator(g)) for g in self.population]
            scored.sort(key=lambda x: x[1], reverse=True)
            
            best = scored[0]
            avg = sum(s[1] for s in scored) / len(scored)
            self.history["bf"].append(best[1])
            
            # 3. 多样性
            div = np.std([s[0] for s in scored], axis=0).mean()
            self.history["diversity"].append(div)
            
            # 4. 选择 + 变异 + 交叉
            survivors = [s[0] for s in scored[:max(5, self.pop_size // 3)]]
            new_pop = survivors[:3]  # 精英保护
            
            while len(new_pop) < self.pop_size:
                p1, p2 = random.sample(survivors, 2)
                # 交叉
                child = np.array([p1[i] if random.random() < 0.5 else p2[i] for i in range(genome_dim)])
                # 变异
                for i in range(genome_dim):
                    if random.random() < self.mutation_rate:
                        child[i] += random.gauss(0, 0.1)
                child = np.clip(child, 0, 1)
                new_pop.append(child)
            
            self.population = new_pop
        
        self.history["best_genome"] = max(
            [(g, evaluator(g)) for g in self.population],
            key=lambda x: x[1]
        )[0]
        
        return {
            "task": task,
            "best_fitness": self.history["bf"][-1],
            "generations": self.generations,
            "best_genome": self.history["best_genome"].tolist(),
            "bf_trend": self.history["bf"][-10:]
        }

# 便捷函数
def evolve(task, evaluator, **kwargs):
    """一行调用"""
    agent = EvolveAgent(**kwargs)
    return agent.run(task, evaluator)

if __name__ == "__main__":
    # 演示：优化一个6维函数
    target = np.array([0.8, 0.3, 0.5, 0.9, 0.2, 0.7])
    
    def fitness(genome):
        return 1.0 / (1.0 + np.linalg.norm(genome - target))
    
    result = evolve("向目标向量收敛", fitness, pop_size=30, generations=50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
