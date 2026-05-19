"""Tim cac chuoi gay Belady cho FIFO."""
import random
from algorithms import fifo

CANDIDATES = [
    # cac chuoi co dien / bien the
    "1 2 3 4 1 2 5 1 2 3 4 5",          # goc
    "3 2 1 0 3 2 4 3 2 1 0 4",
    "4 3 2 1 4 3 5 4 3 2 1 5",
    "1 2 3 4 5 6 1 2 3 4 5 6",
    "0 1 2 3 0 1 4 0 1 2 3 4",
    "5 4 3 2 1 5 4 6 5 4 3 2 1 6",
    "2 3 4 5 2 3 6 2 3 4 5 6",
    "1 2 3 4 1 2 5 1 2 3 4 5 6 1 2 3 4 5 6",
]

def faults_for(seq, cap):
    return fifo([int(x) for x in seq.split()], cap)["faults"]

def has_belady(seq, frames=range(1, 8)):
    fs = [faults_for(seq, c) for c in frames]
    pairs = []
    for i in range(len(fs) - 1):
        if fs[i + 1] > fs[i]:
            pairs.append((list(frames)[i], list(frames)[i + 1], fs[i], fs[i + 1]))
    return fs, pairs

print("=== Cac chuoi co san ===")
for s in CANDIDATES:
    fs, pairs = has_belady(s)
    print(f"{s!r}\n  faults theo frame 1..7 = {fs}\n  Belady: {pairs}\n")

# Tim them ngau nhien
print("=== Sinh ngau nhien (tim 5 chuoi moi) ===")
random.seed(42)
found = 0
tries = 0
while found < 5 and tries < 5000:
    tries += 1
    n = random.randint(10, 16)
    k = random.randint(4, 6)         # so trang khac nhau
    seq = " ".join(str(random.randint(1, k)) for _ in range(n))
    fs, pairs = has_belady(seq, frames=range(2, 6))
    if pairs:
        # uu tien chuoi co Belady o 3->4
        if any(p[0] == 3 and p[1] == 4 for p in pairs):
            print(f"{seq}\n  faults frame 2..5 = {fs}\n  Belady: {pairs}\n")
            found += 1
