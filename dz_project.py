import threading
import queue

#  РОБОЧИЙ ПОТІК

class WorkerThread(threading.Thread):
    def __init__(self, idx: int, q: queue.Queue):
        super().__init__(daemon=True)
        self.idx = idx
        self.q = q

    def run(self):
        while True:
            msg = self.q.get()
            try:
                if msg is None:
                    print(f"Thread {self.idx}: отримано сигнал завершення. Виходжу.", flush=True)
                    break
                print(f"Thread {self.idx}: {msg}", flush=True)
            finally:
                self.q.task_done()

#  УПРАВЛЯЮЧИЙ ПОТІК

class ControllerThread(threading.Thread):
    def __init__(self, out_queue: queue.Queue):
        super().__init__(daemon=True)
        self.out_queue = out_queue

    def run(self):
        print("Управляючий потік запущено. Введіть 'quit' для завершення.")
        while True:
            try:
                target = input("Введіть номер потоку (1..3), 'all' або 'quit': ").strip()
            except EOFError:
                target = 'quit'

            if target.lower() == 'quit':
                self.out_queue.put({'n': 'quit', 't': ''})
                break

            if target == '':
                print("Порожнє введення — спробуйте знову.")
                continue

            text = input("Введіть текст повідомлення: ").strip()
            # Створюємо словник повідомлення
            msg = {'n': target, 't': text}

            # Вивід для підтвердження створення словника
            print(f"Створено словник повідомлення: {msg}")

            # Відправляємо словник головному потоку
            self.out_queue.put(msg)


#  ТОЧКА ВХОДУ

if __name__ == '__main__':
    num_workers = 3

    # Створюємо чергу для кожного робочого потоку
    worker_queues = [queue.Queue() for _ in range(num_workers)]
    workers = [WorkerThread(i+1, q) for i, q in enumerate(worker_queues)]
    for w in workers:
        w.start()

    # Черга для передачі від ControllerThread до main
    controller_queue = queue.Queue()
    controller = ControllerThread(controller_queue)
    controller.start()

    try:
        while True:
            # Головний потік отримує повідомлення з контролера
            msg = controller_queue.get()
            n = msg['n']
            text = msg['t']

            if n == 'quit':
                # Сигнал завершення — надсилаємо None у всі робочі потоки
                for q in worker_queues:
                    q.put(None)
                break

            # Надсилання повідомлення у потрібну чергу або broadcast
            if n.lower() == 'all':
                for q in worker_queues:
                    q.put({'n': 'all', 't': text})
            else:
                try:
                    idx = int(n) - 1
                    if 0 <= idx < num_workers:
                        worker_queues[idx].put({'n': int(n), 't': text})
                    else:
                        print("Невірний номер потоку.")
                except ValueError:
                    print("Введіть число або 'all'.")

            controller_queue.task_done()

    except KeyboardInterrupt:
        print("\nCtrl+C — надсилаю сигнали завершення.")
        for q in worker_queues:
            q.put(None)

    # Чекаємо завершення всіх черг
    for q in worker_queues:
        q.join()

    print("Main: усі робочі потоки завершено. Вихід.")
