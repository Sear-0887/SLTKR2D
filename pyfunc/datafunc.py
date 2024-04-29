def capitalize(s):
    s=s[0].upper()+s[1:]
    return s

def plural(s):
    if s.endswith('y'): # just in case
        s=s[:-1]+'ie'
    s+="s"
    return s

def past(s):
    if s.endswith('e'):
        s=s[:-1]
    s+="ed"
    return s

def tuple_max(*tuples) -> tuple[int]:
    return tuple(map(max, zip(*tuples)))
def tuple_min(*tuples) -> tuple[int]:
    return tuple(map(min, zip(*tuples)))