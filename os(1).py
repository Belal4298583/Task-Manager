import threading
import queue
import time
import random


resources = {}
resource_locks = {}


ready_queues = {
    'P1': queue.Queue(),
    'P2': queue.Queue(),
    'P3': queue.Queue()
}
waiting_queue = queue.Queue()


tasks = []

def read_input():
    global resources, tasks


    resources['R1'] = int(input("Enter the number of R1 resources: "))
    resources['R2'] = int(input("Enter the number of R2 resources: "))
    resources['R3'] = int(input("Enter the number of R3 resources: "))

    for res in resources:
        resource_locks[res] = threading.Lock()


    num_tasks = int(input("Enter the number of tasks: "))
    for i in range(num_tasks):
        task_id = f"T{i+1}"
        period = random.randint(10, 100)
        execution_time = random.randint(1, period)
        repeat = random.randint(1, 5)
        num_resources = random.randint(1, 3)
        task_resources = {}
        for j in range(num_resources):
            res_type = random.choice(['R1', 'R2', 'R3'])
            res_amount = random.randint(1, resources[res_type])
            task_resources[res_type] = res_amount
        tasks.append({
            'id': task_id,
            'period': period,
            'execution_time': execution_time,
            'resources': task_resources,
            'repeat': repeat,
            'initial_execution_time': execution_time
        })

class MainThread(threading.Thread):
    def __init__(self, processors):
        threading.Thread.__init__(self)
        self.processors = processors
   
    def run(self):
        time_unit = 0
        while True:
            print(f"Time: {time_unit}")
            print("\n========== Current Status ==========")
            print("Resources:")
            for res, amount in resources.items():
                print(f"  {res}: {amount}")
            print("\nWaiting Queue:")
            for task in list(waiting_queue.queue):
                print(f"  {task['id']} (Remaining: {task['repeat']})")
            print("\nReady Queues:")
            for pid, q in ready_queues.items():
                queue_list = list(q.queue)
                task_counts = {task['id']: 0 for task in queue_list}
                for task in queue_list:
                    task_counts[task['id']] += 1
                ready_queue_str = ', '.join([f"{tid}:{count}" for tid, count in task_counts.items()])
                print(f"  {pid}: [{ready_queue_str}]")
            for processor in self.processors:
                print(f"\nCPU{processor.id}:")
                print(f"CPU Utilization: {min(processor.utilization, 100):.2f}%")
                queue_list = list(ready_queues[processor.id].queue)
                task_counts = {task['id']: 0 for task in queue_list}
                for task in queue_list:
                    task_counts[task['id']] += 1
                ready_queue_str = ', '.join([f"{tid}:{count}" for tid, count in task_counts.items()])
                print(f"Ready Queue: [{ready_queue_str}]")
                if processor.running_task:
                    print(f"Running Task: {processor.running_task['id']}")
                else:
                    print("Running Task: None")
            print("====================================\n")
            time_unit += 1
            time.sleep(2)

class ProcessorThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
        self.utilization = 0
        self.running_task = None
   
    def run(self):
        while True:
            if not ready_queues[self.id].empty():
                task = ready_queues[self.id].get()
                self.execute_task(task)
            else:
                if not waiting_queue.empty():
                    task = waiting_queue.get()
                    self.execute_task(task)
            time.sleep(1)  

    def execute_task(self, task):
        required_resources = task['resources']
        for res in required_resources:
            with resource_locks[res]:
                if resources[res] >= required_resources[res]:
                    resources[res] -= required_resources[res]
                else:
                    waiting_queue.put(task)
                    return
       
        print(f"Processor {self.id} is executing task {task['id']}")
        self.running_task = task
        utilization_increment = (task['initial_execution_time'] / task['period']) * 100
        self.utilization = min(utilization_increment, 100)
        time.sleep(task['execution_time'])
       
        for res in required_resources:
            with resource_locks[res]:
                resources[res] += required_resources[res]

        self.running_task = None
        task['repeat'] -= 1
        if task['repeat'] > 0:
            ready_queues[self.id].put(task)

def start_threads():
    processors = [ProcessorThread(f'P{i+1}') for i in range(3)]
    main_thread = MainThread(processors)
    main_thread.start()
    for pt in processors:
        pt.start()
    return processors

def distribute_tasks(algorithm):
    if algorithm == 'EDF':
        tasks.sort(key=lambda x: x['period'])
    elif algorithm == 'RateMonotonic':
        tasks.sort(key=lambda x: x['period'])
   
    for i, task in enumerate(tasks):
        for _ in range(task['repeat']): 
            ready_queues[f'P{(i % 3) + 1}'].put(task)

def main():
    read_input()
    processors = start_threads()
    distribute_tasks(algorithm='EDF')  # 'EDF' یا 'RateMonotonic'

if __name__ == "__main__":
    main()
