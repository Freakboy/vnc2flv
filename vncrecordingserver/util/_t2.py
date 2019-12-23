import os
import threading
import ctypes
import time
import requests


def pthread_level1(i):
    print("workor id :%s" % i)

    # 获取threading对象的标识ident
    print(threading.currentThread())

    print(threading.currentThread().ident)
    print("threaing id: ", ctypes.CDLL('libc.so.6').syscall(186))

    d = requests.get("http://www.google.com")
    time.sleep(100)
    return


if __name__ == "__main__":
    l = []
    for i in range(5):
        t = threading.Thread(target=pthread_level1, args=(i,))
        l.append(t)
    for i in l:
        i.start()
    # 查看进程跟线程的关系
    os.system("pstree -p " + str(os.getpid()))
    for i in l:
        i.join()

    print("Sub-process done.")