
def location(block):
    # Your code here


def temperature(block):
    # Your code here


def x_coordinate(block):
    # Your code here


def y_coordinate(block):
    # Your code here


def pressure(block):
    # Your code here


def get_block(data):
    # Your code here


def main():
    data = input('Enter the raw data:\n')
    block = get_block(data)
    print('Site information:')
    print('Location:', location(block))
    print('Coordinates:', y_coordinate(block), x_coordinate(block))
    print('Temperature: {:.2f} C'.format(temperature(block)))
    print('Pressure: {:.2f} hPa'.format(pressure(block)))

if __name__=='__main__':
    main()
