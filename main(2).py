import threading
import queue
import time
import random
import tkinter as tk
from tkinter import ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
        task_resources = {}
        for res in resources:
            task_resources[res] = random.randint(0, resources[res])  

        tasks.append({
            'id': task_id,
            'period': period,
            'execution_time': execution_time,
            'resources': task_resources,
            'repeat': repeat,
            'initial_execution_time': execution_time
        })


class MainThread(threading.Thread):
    def __init__(self, processors, gui):
        threading.Thread.__init__(self)
        self.processors = processors
        self.gui = gui

    def run(self):
        time_unit = 0
        while True:
            time_unit += 1
            self.gui.update_status(time_unit)
            time.sleep(1)

class ProcessorThread(threading.Thread):
    def __init__(self, id, processors):
        threading.Thread.__init__(self)
        self.id = id
        self.utilization = 0
        self.utilization_history = []  
        self.running_task = None
        self.processors = processors

    def run(self):
        while True:
            if not ready_queues[self.id].empty():
                task = ready_queues[self.id].get()
                self.execute_task(task)
            else:
                self.load_balance()
                if not waiting_queue.empty():
                    task = waiting_queue.get()
                    self.execute_task(task)
            time.sleep(0.1)

    def load_balance(self):
        for processor in self.processors:
            if processor.id != self.id and not ready_queues[processor.id].empty():
                task = ready_queues[processor.id].get()
                ready_queues[self.id].put(task)
                break

    def execute_task(self, task):
        required_resources = task['resources']
        acquired_locks = []
        try:
            
            for res in required_resources:
                resource_locks[res].acquire()
                acquired_locks.append(res)
                if resources[res] < required_resources[res]:
                    raise RuntimeError(f"Not enough {res}")
                resources[res] -= required_resources[res]

            
            print(f"Processor {self.id} is executing task {task['id']}")
            self.running_task = task
            utilization_increment = (task['initial_execution_time'] / task['period']) * 100
            self.utilization = min(utilization_increment, 100)
            self.utilization_history.append(self.utilization)  
            time.sleep(task['execution_time']/10)

            
            for res in required_resources:
                resources[res] += required_resources[res]

        except RuntimeError as e:
            print(e)
            waiting_queue.put(task)
        finally:
            for res in acquired_locks:
                resource_locks[res].release()

        self.running_task = None
        task['repeat'] -= 1
        if task['repeat'] > 0:
            ready_queues[self.id].put(task)

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduling System")

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.resource_label = ttk.Label(self.main_frame, text="Resources:")
        self.resource_label.grid(row=0, column=0, sticky=tk.W)

        self.resource_text = tk.Text(self.main_frame, width=50, height=5)
        self.resource_text.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.waiting_queue_label = ttk.Label(self.main_frame, text="Waiting Queue:")
        self.waiting_queue_label.grid(row=2, column=0, sticky=tk.W)

        self.waiting_queue_text = tk.Text(self.main_frame, width=50, height=5)
        self.waiting_queue_text.grid(row=3, column=0, sticky=(tk.W, tk.E))

        self.ready_queue_label = ttk.Label(self.main_frame, text="Ready Queues:")
        self.ready_queue_label.grid(row=4, column=0, sticky=tk.W)

        self.ready_queue_text = tk.Text(self.main_frame, width=50, height=5)
        self.ready_queue_text.grid(row=5, column=0, sticky=(tk.W, tk.E))

        self.cpu_frames = {}
        self.cpu_plots = {}
        for i in range(1, 4):
            cpu_frame = ttk.Frame(self.main_frame, padding="5", borderwidth=2, relief="sunken")
            cpu_frame.grid(row=0, column=1+i, sticky=(tk.W, tk.E))
            self.cpu_frames[f'P{i}'] = cpu_frame

            ttk.Label(cpu_frame, text=f"CPU {i}:").grid(row=0, column=0, sticky=tk.W)
            ttk.Label(cpu_frame, text="CPU Utilization:").grid(row=1, column=0, sticky=tk.W)
            self.cpu_frames[f'P{i}_util'] = ttk.Label(cpu_frame, text="0%")
            self.cpu_frames[f'P{i}_util'].grid(row=1, column=1, sticky=tk.W)

            ttk.Label(cpu_frame, text="Ready Queue:").grid(row=2, column=0, sticky=tk.W)
            self.cpu_frames[f'P{i}_ready'] = ttk.Label(cpu_frame, text="")
            self.cpu_frames[f'P{i}_ready'].grid(row=2, column=1, sticky=tk.W)

            ttk.Label(cpu_frame, text="Running Task:").grid(row=3, column=0, sticky=tk.W)
            self.cpu_frames[f'P{i}_running'] = ttk.Label(cpu_frame, text="None")
            self.cpu_frames[f'P{i}_running'].grid(row=3, column=1, sticky=tk.W)

            
            fig, ax = plt.subplots(figsize=(3, 2), tight_layout=True)
            self.cpu_plots[f'P{i}'] = ax
            self.cpu_frames[f'P{i}_plot'] = FigureCanvasTkAgg(fig, master=cpu_frame)
            self.cpu_frames[f'P{i}_plot'].get_tk_widget().grid(row=4, column=0, columnspan=2)

    def update_status(self, time_unit):
        self.resource_text.delete('1.0', tk.END)
        for res, amount in resources.items():
            self.resource_text.insert(tk.END, f"{res}: {amount}\n")

        self.waiting_queue_text.delete('1.0', tk.END)
        for task in list(waiting_queue.queue):
            self.waiting_queue_text.insert(tk.END, f"{task['id']} (Remaining: {task['repeat']})\n")

        self.ready_queue_text.delete('1.0', tk.END)
        for pid, q in ready_queues.items():
            queue_list = list(q.queue)
            task_counts = {task['id']: 0 for task in queue_list}
            for task in queue_list:
                task_counts[task['id']] += 1
            ready_queue_str = ', '.join([f"{tid}:{count}" for tid, count in task_counts.items()])
            self.ready_queue_text.insert(tk.END, f"{pid}: [{ready_queue_str}]\n")

        for i in range(1, 4):
            processor = self.processors[f'P{i}']
            self.cpu_frames[f'P{i}_util'].config(text=f"{min(processor.utilization, 100):.2f}%")
            queue_list = list(ready_queues[processor.id].queue)
            task_counts = {task['id']: 0 for task in queue_list}
            for task in queue_list:
                task_counts[task['id']] += 1
            ready_queue_str = ', '.join([f"{tid}:{count}" for tid, count in task_counts.items()])
            self.cpu_frames[f'P{i}_ready'].config(text=ready_queue_str)
            if processor.running_task:
                self.cpu_frames[f'P{i}_running'].config(text=processor.running_task['id'])
            else:
                self.cpu_frames[f'P{i}_running'].config(text="None")

            
            ax = self.cpu_plots[f'P{i}']
            ax.clear()
            ax.plot(range(len(processor.utilization_history)), processor.utilization_history)  
            ax.set_title(f'CPU {i} Utilization')
            ax.set_xlabel('Time')
            ax.set_ylabel('Utilization (%)')
            self.cpu_frames[f'P{i}_plot'].draw()

    def set_processors(self, processors):
        self.processors = processors


def start_threads(gui):
    processors = [ProcessorThread(f'P{i+1}', None) for i in range(3)]
    for processor in processors:
        processor.processors = processors
    main_thread = MainThread(processors, gui)
    main_thread.start()
    for pt in processors:
        pt.start()
    gui.set_processors({f'P{i+1}': pt for i, pt in enumerate(processors)})
    return processors

def distribute_tasks(algorithm):
    if algorithm == 'EDF':
        tasks.sort(key=lambda x: x['period'])
    elif algorithm == 'RateMonotonic':
        tasks.sort(key=lambda x: x['period'])

    for i, task in enumerate(tasks):
        for _ in range(task['repeat']):
            ready_queues[f'P{(i % 3) + 1}'].put(task)

def age_tasks():
    while True:
        
        with waiting_queue.mutex:
            for task in list(waiting_queue.queue):
                task['period'] -= 1
                if task['period'] <= 0:
                    ready_queues[f'P{random.randint(1, 3)}'].put(task)
                    waiting_queue.queue.remove(task)

def main():
    read_input()

    root = tk.Tk()
    gui = GUI(root)

    processors = start_threads(gui)
    distribute_tasks(algorithm='R')
    aging_thread = threading.Thread(target=age_tasks)
    aging_thread.start()

    root.mainloop()

if __name__ == "__main__":
    main()
