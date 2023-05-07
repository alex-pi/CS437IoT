from request_controller import RequestController
import sys


def get_params():
    print(sys.argv[1])
    if len(sys.argv) < 3:
        print("Not enough parameters.")
        sys.exit(1)
    plant = sys.argv[1]
    mils = int(sys.argv[2])

    return {
        'cmd': 'water',
        'params': {
            'ml': mils,
            'plant': plant
        }
    }


if __name__ == '__main__':
    rcm = RequestController()
    rcm.handle(get_params())
