# simulation/simulation_runner.py
import os
import csv
from simulation.simulation import run_simulation_once
import random

OUTDIR = 'simulation/precomputed_results'
os.makedirs(OUTDIR, exist_ok=True)

def baseline_params():
    def p1(): return max(0.1, random.normalvariate(10,1.5))
    def p2(): return max(0.1, random.normalvariate(8,1.0))
    def p3(): return max(0.1, random.normalvariate(6,0.5))
    return {
        'arrival_rate': 1/20.0,  # jobs per minute
        'mttf': [200.0, 300.0, 400.0],
        'mttr': [40.0, 30.0, 30.0],
        'process_times': [p1,p2,p3]
    }

def connected_params():
    def p1(): return max(0.1, random.normalvariate(9,1.2))
    def p2(): return max(0.1, random.normalvariate(7.5,0.9))
    def p3(): return max(0.1, random.normalvariate(5.5,0.4))
    return {
        'arrival_rate': 1/18.0,
        'mttf': [300.0, 450.0, 600.0],
        'mttr': [30.0, 20.0, 20.0],
        'process_times': [p1,p2,p3]
    }

def predictive_params():
    def p1(): return max(0.1, random.normalvariate(8.5,1.0))
    def p2(): return max(0.1, random.normalvariate(7.0,0.8))
    def p3(): return max(0.1, random.normalvariate(5.0,0.3))
    return {
        'arrival_rate': 1/16.0,
        'mttf': [600.0, 900.0, 1200.0],
        'mttr': [15.0, 12.0, 10.0],
        'process_times': [p1,p2,p3]
    }

SCENARIOS = {
    'level1_baseline': baseline_params,
    'level3_connected': connected_params,
    'level4_predictive': predictive_params
}

def run_and_save(n_rep=30, sim_time_min=8*60):
    for name, params_fn in SCENARIOS.items():
        out_csv = os.path.join(OUTDIR, f'{name}.csv')
        print(f'Running scenario {name} -> {out_csv}')
        with open(out_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['rep','throughput_per_hr','avg_lead_time_min','generated','completed'])
            for rep in range(1, n_rep+1):
                seed = rep * 100 + 7
                random.seed(seed)
                params = params_fn()
                res = run_simulation_once(params, sim_time_minutes=sim_time_min, seed=seed)
                writer.writerow([rep, res['throughput_per_hr'], res['avg_lead_time_min'], res['generated'], res['completed']])
        print(f'Wrote {out_csv}')

if __name__ == '__main__':
    run_and_save(n_rep=30, sim_time_min=8*60)
    print('All scenarios done.')
