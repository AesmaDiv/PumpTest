line_count = 0
is_enabled = True
is_even = False
addendum = 2


def func():
    if is_enabled:
        global line_count
        line_count += addendum if is_even else 1
    print(line_count)


func()
