from datetime import datetime


def log(message: str):
    with open('log.txt', 'a') as file:
        file.write(f'\n\n{datetime.now()}: {message}\n')


if __name__ == '__main__':
    log('StartLogging')
