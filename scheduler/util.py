def make_string_short(string, n):
    if len(string) > n:
        return string[: n - 3] + "..."
    return string[:n]
