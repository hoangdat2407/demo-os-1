"""
Cac thuat toan thay the trang (page replacement algorithms)

Moi ham nhan:
    pages  : list[int]   - chuoi tham chieu trang
    capacity: int        - so frame
Tra ve dict:
    {
        "faults":  so lan page fault,
        "hits":    so lan hit,
        "steps":   list cac buoc, moi buoc:
            {
                "page":  trang dang truy cap,
                "frames": list trang trong frame sau buoc nay (do dai = capacity, None neu trong),
                "fault": True/False,
                "victim": trang bi thay (None neu khong thay),
                "note":   ghi chu them (vd: bit tham chieu, tan suat...)
            }
    }
"""

from collections import deque, Counter


def _empty_frames(capacity):
    return [None] * capacity


def _snapshot(frames):
    # tra ve mot ban sao (de luu tung buoc)
    return list(frames)


# ---------------------------------------------------------------------------
# 1. FIFO - First In First Out
# ---------------------------------------------------------------------------
def fifo(pages, capacity):
    frames = _empty_frames(capacity)
    queue = deque()          # thu tu vao
    faults = hits = 0
    steps = []

    for p in pages:
        fault = False
        victim = None
        note = ""

        if p in frames:
            hits += 1
        else:
            fault = True
            faults += 1
            if None in frames:
                idx = frames.index(None)
                frames[idx] = p
                queue.append(p)
            else:
                victim = queue.popleft()
                idx = frames.index(victim)
                frames[idx] = p
                queue.append(p)
            note = "Hàng đợi: " + " -> ".join(str(x) for x in queue)
        # print(frames)
        steps.append({
            "page": p,
            "frames": _snapshot(frames),
            "fault": fault,
            "victim": victim,
            "note": note,
        })

    return {"faults": faults, "hits": hits, "steps": steps}


# ---------------------------------------------------------------------------
# 2. Optimal - thay trang dung xa nhat trong tuong lai
# ---------------------------------------------------------------------------
def optimal(pages, capacity):
    frames = _empty_frames(capacity)
    faults = hits = 0
    steps = []

    for i, p in enumerate(pages):
        fault = False
        victim = None
        note = ""

        if p in frames:
            hits += 1
        else:
            fault = True
            faults += 1
            if None in frames:
                idx = frames.index(None)
                frames[idx] = p
            else:
                # tim trang co lan dung tiep theo xa nhat (hoac khong dung nua)
                farthest = -1
                replace_idx = 0
                for j, f in enumerate(frames):
                    try:
                        nxt = pages.index(f, i + 1)
                    except ValueError:
                        nxt = float("inf")  # khong dung nua -> uu tien thay
                    if nxt > farthest:
                        farthest = nxt
                        replace_idx = j
                victim = frames[replace_idx]
                frames[replace_idx] = p
                note = "Thay {} (đứng xa nhất)".format(victim)

        steps.append({
            "page": p,
            "frames": _snapshot(frames),
            "fault": fault,
            "victim": victim,
            "note": note,
        })

    return {"faults": faults, "hits": hits, "steps": steps}


# ---------------------------------------------------------------------------
# 3. LRU - Least Recently Used
# ---------------------------------------------------------------------------
def lru(pages, capacity):
    frames = _empty_frames(capacity)
    last_used = {}           # page -> chi so lan dung gan nhat
    faults = hits = 0
    steps = []

    for i, p in enumerate(pages):
        fault = False
        victim = None

        if p in frames:
            hits += 1
        else:
            fault = True
            faults += 1
            if None in frames:
                idx = frames.index(None)
                frames[idx] = p
            else:
                # tim trang co last_used nho nhat
                victim = frames[0]
                for f in frames[1:]:
                    if last_used[victim] > last_used[f]:
                        victim = f
                idx = frames.index(victim)
                frames[idx] = p

        last_used[p] = i
        note = "Lần dùng gần nhất: " + ", ".join(
            "{} -> {}".format(f, last_used[f]) for f in frames if f is not None
        )

        steps.append({
            "page": p,
            "frames": _snapshot(frames),
            "fault": fault,
            "victim": victim,
            "note": note,
        })

    return {"faults": faults, "hits": hits, "steps": steps}


# ---------------------------------------------------------------------------
# 4. MRU - Most Recently Used
# ---------------------------------------------------------------------------
def mru(pages, capacity):
    frames = _empty_frames(capacity)
    last_used = {}
    faults = hits = 0
    steps = []

    for i, p in enumerate(pages):
        fault = False
        victim = None

        if p in frames:
            hits += 1
        else:
            fault = True
            faults += 1
            if None in frames:
                idx = frames.index(None)
                frames[idx] = p
            else:
                # tim trang co last_used lon nhat (vua dung gan day nhat)
                victim = frames[0]
                for f in frames[1:]:
                    if last_used[victim] < last_used[f]:
                        victim = f
                idx = frames.index(victim)
                frames[idx] = p

        last_used[p] = i
        note = "Thay trang vừa dùng gần nhất"

        steps.append({
            "page": p,
            "frames": _snapshot(frames),
            "fault": fault,
            "victim": victim,
            "note": note,
        })

    return {"faults": faults, "hits": hits, "steps": steps}


# ---------------------------------------------------------------------------
# 5. LFU - Least Frequently Used (tie-break: vao truoc thay truoc)
# ---------------------------------------------------------------------------
def lfu(pages, capacity):
    frames = _empty_frames(capacity)
    freq = Counter()
    arrival = {}              # thoi diem nap (de break tie)
    faults = hits = 0
    steps = []

    for i, p in enumerate(pages):
        fault = False
        victim = None

        if p in frames:
            hits += 1
            freq[p] += 1
        else:
            fault = True
            faults += 1
            if None in frames:
                idx = frames.index(None)
                frames[idx] = p
            else:
                # min freq, tie -> arrival nho nhat (cu nhat)
                victim = frames[0]
                for f in frames[1:]:
                    if freq[f] < freq[victim]:
                        victim = f
                    elif freq[f] == freq[victim]:
                        if arrival[f] < arrival[victim]:
                            victim = f
                idx = frames.index(victim)
                del freq[victim]
                del arrival[victim]
                frames[idx] = p
            freq[p] = 1
            arrival[p] = i

        note = "Tần suất: " + ", ".join(
            "{}={}".format(f, freq[f]) for f in frames if f is not None
        )

        steps.append({
            "page": p,
            "frames": _snapshot(frames),
            "fault": fault,
            "victim": victim,
            "note": note,
        })

    return {"faults": faults, "hits": hits, "steps": steps}


# ---------------------------------------------------------------------------
# 6. MFU - Most Frequently Used (tie-break: vao truoc thay truoc)
# ---------------------------------------------------------------------------
def mfu(pages, capacity):
    frames = _empty_frames(capacity)
    freq = Counter()
    arrival = {}
    faults = hits = 0
    steps = []

    for i, p in enumerate(pages):
        fault = False
        victim = None

        if p in frames:
            hits += 1
            freq[p] += 1
        else:
            fault = True
            faults += 1
            if None in frames:
                idx = frames.index(None)
                frames[idx] = p
            else:
                # max freq, tie -> arrival nho nhat
                victim = frames[0]
                for f in frames[1:]:
                    if freq[f] > freq[victim]:
                        victim = f
                    elif freq[f] == freq[victim]:
                        if arrival[f] > arrival[victim]:
                            victim = f
                idx = frames.index(victim)
                del freq[victim]
                del arrival[victim]
                frames[idx] = p
            freq[p] = 1
            arrival[p] = i

        note = "Tần suất: " + ", ".join(
            "{}={}".format(f, freq[f]) for f in frames if f is not None
        )

        steps.append({
            "page": p,
            "frames": _snapshot(frames),
            "fault": fault,
            "victim": victim,
            "note": note,
        })

    return {"faults": faults, "hits": hits, "steps": steps}


# ---------------------------------------------------------------------------
# 7. Second Chance - FIFO + reference bit
# ---------------------------------------------------------------------------
def second_chance(pages, capacity):
    # dung deque cac cap (page, ref_bit) theo thu tu FIFO
    queue = deque()
    faults = hits = 0
    steps = []

    def frames_view():
        # tra ve list co dinh do dai = capacity
        view = [item[0] for item in queue]
        while len(view) < capacity:
            view.append(None)
        return view

    for p in pages:
        fault = False
        victim = None
        note = ""

        # kiem tra hit
        hit = False
        for i, (pg, _) in enumerate(queue):
            if pg == p:
                queue[i] = (pg, 1)        # set bit tham chieu
                hit = True
                break

        if hit:
            hits += 1
        else:
            fault = True
            faults += 1
            if len(queue) < capacity:
                queue.append((p, 0))
            else:
                # tim victim: duyet vong, neu bit=1 -> set 0 va day xuong cuoi,
                # neu bit=0 -> thay
                while True:
                    pg, bit = queue.popleft()
                    if bit == 0:
                        victim = pg
                        queue.append((p, 0))
                        break
                    else:
                        queue.append((pg, 0))   # cho them co hoi

        note = "Bit tham chiếu: " + ", ".join(
            "{}={}".format(pg, bit) for pg, bit in queue
        )

        steps.append({
            "page": p,
            "frames": frames_view(),
            "fault": fault,
            "victim": victim,
            "note": note,
        })

    return {"faults": faults, "hits": hits, "steps": steps}


# ---------------------------------------------------------------------------
# Bang dieu phoi
# ---------------------------------------------------------------------------
ALGORITHMS = {
    "FIFO":          fifo,
    "Optimal":       optimal,
    "LRU":           lru,
    "MRU":           mru,
    "LFU":           lfu,
    "MFU":           mfu,
    "Second Chance": second_chance,
}


def run(name, pages, capacity):
    """Chay thuat toan theo ten."""
    if name not in ALGORITHMS:
        raise ValueError("Không có thuật toán: " + name)
    return ALGORITHMS[name](pages, capacity)
