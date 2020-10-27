# this file is unrelated to the project, used for testing scripts

def XPattern(size=20):
    ret = [[0 for i in range(32)] for j in range(32)]
    for row in range((32-size)//2, (32-size)//2+size):
        for col in range((32-size)//2, (32-size)//2+size):
            if row - col == 0:
                ret[row][col] = 1
            elif row + col == 31:
                ret[row][col] = 1
    return ret


def UPattern(size=20):
    ret = [[0 for i in range(32)] for j in range(32)]
    col = (32-size)//2
    for row in range((32-size)//2, (32-size)//2+size):
        ret[row][col] = 1

    col = (32-size)//2+size
    for row in range((32-size)//2, (32-size)//2+size):
        ret[row][col] = 1
    
    row = (32-size)//2+size
    for col in range((32-size)//2, (32-size)//2+size+1):
        ret[row][col] = 1

    return ret

for row in UPattern():
    print(row)