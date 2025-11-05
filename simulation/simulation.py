# simulation/simulation.py
import simpy
import random
import statistics

class Machine:
    def __init__(self, env, name, mttf, mttr):
        self.env = env
        self.name = name
        self.mttf = mttf
        self.mttr = mttr
        self.resource = simpy.Resource(env, capacity=1)
        self.busy_time = 0.0
        self.downtime = 0.0
        self.next_failure_time = None
        self.failed = False
        self.schedule_next_failure()

    def schedule_next_failure(self):
        ttf = random.expovariate(1.0 / self.mttf)
        self.next_failure_time = self.env.now + max(0.0001, ttf)

    def fail_and_repair(self):
        self.failed = True
        down_start = self.env.now
        repair_time = random.expovariate(1.0 / self.mttr)
        yield self.env.timeout(repair_time)
        self.failed = False
        self.downtime += self.env.now - down_start
        self.schedule_next_failure()

def machine_failure_monitor(env, machine):
    while True:
        wait = max(0.0, machine.next_failure_time - env.now)
        yield env.timeout(wait)
        # start repair process
        yield env.process(machine.fail_and_repair())

def job_process(env, job_id, machines, process_times, stats):
    arrival = env.now
    for i, machine in enumerate(machines):
        proc_time = max(0.01, process_times[i]())
        with machine.resource.request() as req:
            yield req
            remaining = proc_time
            while remaining > 1e-6:
                if machine.failed:
                    # wait until machine repaired
                    yield env.timeout(0.1)
                    continue
                t_until_fail = machine.next_failure_time - env.now
                if t_until_fail <= 0:
                    # allow failure monitor to handle immediate failure
                    yield env.timeout(0.0)
                    continue
                step = min(remaining, t_until_fail)
                yield env.timeout(step)
                remaining -= step
            machine.busy_time += proc_time
    stats['completed_times'].append(env.now - arrival)
    stats['completion_times'].append(env.now)

def job_generator(env, arrival_rate, machines, process_times, sim_time, stats):
    job_id = 0
    while env.now < sim_time:
        inter = random.expovariate(arrival_rate)
        yield env.timeout(inter)
        job_id += 1
        env.process(job_process(env, job_id, machines, process_times, stats))
        stats['generated'] += 1

def run_simulation_once(params, sim_time_minutes=8*60, seed=None):
    if seed is not None:
        random.seed(seed)
    env = simpy.Environment()
    machine_names = ['M1 (CNC)', 'M2 (Finish)', 'Assembly']
    machines = []
    for i, name in enumerate(machine_names):
        mac = Machine(env, name, params['mttf'][i], params['mttr'][i])
        machines.append(mac)
        env.process(machine_failure_monitor(env, mac))

    process_times = params['process_times']
    arrival_rate = params['arrival_rate']

    stats = {'generated':0, 'completed_times':[], 'completion_times':[]}
    env.process(job_generator(env, arrival_rate, machines, process_times, sim_time_minutes, stats))
    env.run(until=sim_time_minutes)

    # KPIs
    throughput_per_hr = len(stats['completion_times']) / (sim_time_minutes/60.0)
    avg_lead_time_min = (statistics.mean(stats['completed_times']) if stats['completed_times'] else None)
    machine_stats = []
    for m in machines:
        util = m.busy_time / sim_time_minutes
        down_frac = m.downtime / sim_time_minutes
        machine_stats.append({
            'name': m.name,
            'busy_time': m.busy_time,
            'downtime': m.downtime,
            'utilization': util,
            'down_frac': down_frac
        })
    return {
        'throughput_per_hr': throughput_per_hr,
        'avg_lead_time_min': avg_lead_time_min,
        'generated': stats['generated'],
        'completed': len(stats['completion_times']),
        'machine_stats': machine_stats
    }
