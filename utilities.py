def safe_int_input(message): #Makes it so that you can't break tghe code by typing in a strong or a float
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Please enter a valid number.")