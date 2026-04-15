lengths = list(range(5))
cumsum = 0
cs = [cumsum := cumsum + x for x in lengths]
print(cs)
print(cumsum)
