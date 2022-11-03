import os

cur_dir = os.path.dirname(__file__)
ways = [cur_dir]
total = 0
without_spaces = 0
while ways:
    filename = ways.pop()
    if os.path.isfile(filename) and filename.endswith('.py') and not filename.endswith('check_lines_of_code.py'):
        with open(filename, 'r') as r:
            for line in r.readlines():
                comment_now = False
                l = line.strip()
                if not comment_now and l.startswith('"""'):
                    comment_now = True
                if comment_now and l.endswith('"""'):
                    comment_now = False
                if l and not l.startswith('#') and not comment_now:
                    without_spaces += 1
                total += 1
    elif os.path.isdir(filename):
        files = os.listdir(filename)
        for file in files:
            ways.append(os.path.join(filename, file))

print(f'Непустые строки: {without_spaces}')
print(f'Всего: {total}')
