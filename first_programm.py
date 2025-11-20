n = int(input())

l = [[""] * n for i in range(n)]

for i in range(n):
    for j in range(n):
        s = int(input())
        l[i][j] = s

mx = 0

for i in range(n):
    for j in range(n):
        if (i + j) <= (i):
            if mx < l[i][j]:
                mx = l[i][j]

print(mx)

