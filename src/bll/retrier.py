from time import sleep


def retry(func, attempts=3, delay=100):
    count = 0
    sleep_time = delay/1000
    while attempts > 0:
        try:
            return func
        except:
            count-=1
            sleep(sleep_time)
            continue
    return None
