#!/usr/bin/env python3
"""
Sanyan Evolve — 工控案例：PID参数自整定

用进化引擎自动优化PID控制器的三个参数（Kp/Ki/Kd）。
无需手动调参——引擎自己找到最优的P/I/D组合。
"""
import numpy as np
from evolve_agent import EvolveAgent

# ============================================================
# PID仿真器（二阶系统）
# ============================================================
def simulate_pid(Kp, Ki, Kd, setpoint=1.0, duration=10.0, dt=0.01):
    """
    仿真PID控制系统响应
    
    Kp: 比例增益
    Ki: 积分增益  
    Kd: 微分增益
    setpoint: 目标值
    duration: 仿真时长（秒）
    dt: 时间步长
    
    返回: ITAE（积分时间绝对误差）——越小越好
    """
    steps = int(duration / dt)
    
    # 二阶系统参数（模拟一个惯性+延迟的工业过程）
    # 例如：温度控制、压力控制、流量控制
    y = 0.0        # 输出
    y_prev = 0.0   # 上一时刻输出
    integral = 0.0
    prev_error = 0.0
    itae = 0.0     # 积分时间绝对误差
    
    for i in range(steps):
        t = i * dt
        error = setpoint - y
        
        # PID计算
        integral += error * dt
        derivative = (error - prev_error) / dt if dt > 0 else 0
        
        u = Kp * error + Ki * integral + Kd * derivative
        
        # 二阶系统模型（离散化）
        # tau=0.5, damping=0.3, gain=0.8
        y_new = (0.8 * u * dt**2 + (2*0.5*0.3*dt + 0.5**2) * y + 0.5 * (2*0.3-2) * dt * y_prev) / (0.5**2 + 2*0.5*0.3*dt + dt**2)
        
        y_prev = y
        y = max(0, min(5, y_new))  # 限幅
        
        prev_error = error
        
        # ITAE：时间加权的绝对误差（后期误差权重更大）
        itae += t * abs(error) * dt
    
    return itae

# ============================================================
# 进化优化
# ============================================================
def optimize_pid(pop_size=40, generations=80):
    """用进化引擎优化PID参数"""
    
    def fitness(genome):
        """genome = [Kp, Ki, Kd]，归一化到[0,1]"""
        Kp = genome[0] * 5.0       # [0, 5]
        Ki = genome[1] * 2.0       # [0, 2]
        Kd = genome[2] * 1.0       # [0, 1]
        
        itae = simulate_pid(Kp, Ki, Kd)
        
        # fitness = 1/(1+ITAE) —— ITAE越小，fitness越高
        return 1.0 / (1.0 + itae)
    
    agent = EvolveAgent(pop_size=pop_size, generations=generations, mutation_rate=0.2)
    result = agent.run("PID参数自整定(Kp/Ki/Kd)", fitness, genome_dim=3)
    
    # 反归一化
    best = result["best_genome"]
    result["Kp"] = round(best[0] * 5.0, 3)
    result["Ki"] = round(best[1] * 2.0, 3)
    result["Kd"] = round(best[2] * 1.0, 3)
    result["ITAE"] = round(1.0/result["best_fitness"] - 1.0, 4)
    
    # 效果评估
    itae_opt = simulate_pid(result["Kp"], result["Ki"], result["Kd"])
    itae_default = simulate_pid(1.0, 0.2, 0.1)  # 默认参数
    
    result["improvement"] = f"{(1-itae_opt/itae_default)*100:.0f}% better than default"
    
    return result

if __name__ == "__main__":
    result = optimize_pid()
    print("=" * 50)
    print("  PID参数自整定 — 进化引擎优化结果")
    print("=" * 50)
    print(f"  Kp = {result['Kp']}")
    print(f"  Ki = {result['Ki']}")
    print(f"  Kd = {result['Kd']}")
    print(f"  ITAE = {result['ITAE']}")
    print(f"  最佳fitness = {result['best_fitness']:.4f}")
    print(f"  进化代数 = {result['generations']}")
    print(f"  效果 = {result['improvement']}")
    print("=" * 50)
