LOG_LEVELS = {
    'ERROR': 0,
    'INFO': 1,
    'DEBUG': 2,
    'TRACE': 3
}

LOG_LVL = 'TRACE'


def trace(message):
    if LOG_LEVELS['TRACE'] <= LOG_LEVELS[LOG_LVL]:
        print(message)


def debug(message):
    if LOG_LEVELS['DEBUG'] <= LOG_LEVELS[LOG_LVL]:
        print(message)


def info(message):
    if LOG_LEVELS['INFO'] <= LOG_LEVELS[LOG_LVL]:
        print(message)


if __name__ == '__main__':
    print()
