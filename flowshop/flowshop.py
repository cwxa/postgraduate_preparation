import random
import os
import matplotlib.pyplot as plt
from typing import List, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class FlowShop2Machine:

    def __init__(self, jobs: List[Tuple[int, int]]):
        self.jobs = jobs
        self.n = len(jobs)

    # ---------------- Johnson 算法 ----------------
    def johnson(self) -> List[int]:
        jobs = list(enumerate(self.jobs))
        left, right = [], []

        while jobs:
            min_job = min(jobs, key=lambda x: min(x[1]))
            idx, (p1, p2) = min_job

            if p1 <= p2:
                left.append(idx)
            else:
                right.append(idx)

            jobs.remove(min_job)

        return left + right[::-1]

    # ---------------- 调度计算 ----------------
    def calculate_schedule(self, sequence: List[int]):
        time_m1 = 0
        time_m2 = 0

        schedule = {"M1": [], "M2": []}
        idle_m2_total = 0

        for job_id in sequence:
            p1, p2 = self.jobs[job_id]

            # M1
            start_m1 = time_m1
            end_m1 = start_m1 + p1
            time_m1 = end_m1

            # M2
            start_m2 = max(time_m2, end_m1)

            if start_m2 > time_m2:
                idle_m2_total += start_m2 - time_m2

            end_m2 = start_m2 + p2
            time_m2 = end_m2

            schedule["M1"].append((job_id, start_m1, p1))
            schedule["M2"].append((job_id, start_m2, p2))

        return schedule, time_m2, idle_m2_total

    # ---------------- 甘特图绘制 ----------------
    def plot_gantt(self, schedule, title, filename):
        plt.figure()

        for machine_index, machine in enumerate(["M1", "M2"]):
            for job_id, start, duration in schedule[machine]:
                plt.barh(machine_index, duration, left=start)
                plt.text(start + duration / 2, machine_index,
                         f"J{job_id}", ha='center', va='center')

        plt.yticks([0, 1], ["Machine 1", "Machine 2"])
        plt.xlabel("Time")
        plt.ylabel("Machine")
        plt.title(title)

        plt.tight_layout()

        save_path = os.path.join(OUTPUT_DIR, filename)
        plt.savefig(save_path)

        print(f"[INFO] Saved Gantt -> {save_path}")

        plt.close()


# ================= 随机实例生成 =================
def generate_random_instance(n, low=1, high=20):
    return [(random.randint(low, high), random.randint(low, high)) for _ in range(n)]


# ================= 单次实验对比 =================
def single_run_demo():
    random.seed(42)
    jobs = generate_random_instance(8)

    model = FlowShop2Machine(jobs)

    johnson_seq = model.johnson()
    rand_seq = list(range(len(jobs)))
    random.shuffle(rand_seq)

    schedule_j, makespan_j, idle_j = model.calculate_schedule(johnson_seq)
    schedule_r, makespan_r, idle_r = model.calculate_schedule(rand_seq)

    print("\n================ JOBS ================")
    print(jobs)

    print("\nJohnson Sequence:", johnson_seq)
    print("Johnson Makespan:", makespan_j)
    print("Johnson Idle(M2):", idle_j)

    print("\nRandom Sequence:", rand_seq)
    print("Random Makespan:", makespan_r)
    print("Random Idle(M2):", idle_r)

    # 甘特图
    model.plot_gantt(schedule_j,
                     "Johnson Schedule Gantt Chart",
                     "johnson_gantt.png")

    model.plot_gantt(schedule_r,
                     "Random Schedule Gantt Chart",
                     "random_gantt.png")


# ================= 多次实验 =================
def experiment(trials=100, n=10):
    johnson_results = []
    random_results = []

    for i in range(trials):
        jobs = generate_random_instance(n)
        model = FlowShop2Machine(jobs)

        seq_j = model.johnson()
        _, mk_j, _ = model.calculate_schedule(seq_j)

        seq_r = list(range(n))
        random.shuffle(seq_r)
        _, mk_r, _ = model.calculate_schedule(seq_r)

        johnson_results.append(mk_j)
        random_results.append(mk_r)

        if (i + 1) % 20 == 0:
            print(f"[INFO] Completed {i+1}/{trials}")

    return johnson_results, random_results


# ================= 主流程 =================
if __name__ == "__main__":

    # 单次对比
    single_run_demo()

    # 多次实验
    johnson_res, random_res = experiment(trials=100, n=10)

    avg_j = sum(johnson_res) / len(johnson_res)
    avg_r = sum(random_res) / len(random_res)

    print("\n================ RESULT ================")
    print("Average Johnson Makespan:", round(avg_j, 2))
    print("Average Random Makespan:", round(avg_r, 2))

    # ================= 对比曲线 =================
    plt.figure()

    plt.plot(johnson_res, label="Johnson")
    plt.plot(random_res, label="Random")

    plt.xlabel("Trial")
    plt.ylabel("Makespan")
    plt.title("Johnson vs Random Makespan Comparison")
    plt.legend()

    plt.tight_layout()

    save_path = os.path.join(OUTPUT_DIR, "johnson_vs_random.png")
    plt.savefig(save_path)

    plt.close()

    print(f"[INFO] Saved Comparison -> {save_path}")

    print("\n================ FILES =================")
    print(f"- {OUTPUT_DIR}/johnson_gantt.png")
    print(f"- {OUTPUT_DIR}/random_gantt.png")
    print(f"- {OUTPUT_DIR}/johnson_vs_random.png")