import threading
import queue
import time
import random

# Кількість другорядних потоків
NUM_WORKERS = 3

# Черга для передачі чисел
task_queue = queue.Queue()

# Другорядний потік
def worker(thread_id, q):
    while True:
        try:
            # Отримуємо число з черги з таймаутом
            number = q.get(timeout=1)
        except queue.Empty:
            # Якщо черга порожня, продовжуємо цикл
            continue

        print(f"Потік {thread_id} отримав число {number}")
        time.sleep(number)  # Затримка на стільки секунд, скільки число
        print(f"Потік {thread_id} завершив очікування")
        q.task_done()

# Створюємо другорядні потоки
threads = []
for i in range(1, NUM_WORKERS + 1):
    t = threading.Thread(target=worker, args=(i, task_queue), daemon=True)
    t.start()
    threads.append(t)

# Управляючий потік
def manager():
    for i in range(10):
        number = random.randint(1, 10)
        print(f"Управляючий потік додає число {number} до черги")
        task_queue.put(number)
        time.sleep(5)  # Кожні 5 секунд генеруємо число

# Запуск управляючого потоку
manager_thread = threading.Thread(target=manager)
manager_thread.start()

# Чекаємо завершення управляючого потоку
manager_thread.join()

# Чекаємо, поки всі завдання у черзі будуть виконані
task_queue.join()

print("Всі завдання виконано.")
