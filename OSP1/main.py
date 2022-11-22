from threading import Thread
import math
from time import perf_counter


file = open("text.txt", "r")
data = file.read()
lines = data.split("\n")
number_of_lines = len(lines)
number_of_threads = 10
load_per_thread = math.ceil(number_of_lines / number_of_threads)


def check(thread_index):
    start_point = load_per_thread * thread_index
    #print(f"Thread #{thread_index} starts at line #{start_point}")
    end_point = start_point + load_per_thread - 1 if start_point + load_per_thread - 1 < number_of_lines else number_of_lines - 1
    #print(f"Thread #{thread_index} ends at line #{end_point}")
    for i in range(start_point, end_point):
        words = lines[i].split(",")
        if words[1] == "pixar" and words[5] == "Ubuntu OS":
            print(f"{i+1}: {lines[i]}")


threads = []
for i in range(number_of_threads):
    t = Thread(target=check, args=(i,))
    threads.append(t)

st = perf_counter()
for t in threads:
    t.start()


for t in threads:
    t.join()

en = perf_counter()
with_thread_time = en - st


st = perf_counter()
for i in range(number_of_lines):
    words = lines[i].split(",")
    if words[1] == "pixar" and words[5] == "Ubuntu OS":
        pass
        #print(f"{i+1}: {lines[i]}")
en = perf_counter()
without_thread_time = en - st


print(f"with thread time:{with_thread_time}\nwithout thread time:{without_thread_time}")



