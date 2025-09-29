with open("big", "w") as file:
    for j in range(100):
        for i in range(1000000):
            file.write("1")
