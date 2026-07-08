
from datetime import datetime


def generate_serial_number():

    now = datetime.now()

    formatted_date = now.strftime('%d_%m_%Y_%H_%M_%S')
    
    return formatted_date

if __name__ == "__main__":
    print(generate_serial_number())

    