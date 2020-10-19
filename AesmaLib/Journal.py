from datetime import date


is_numerated = True
write_to_file = False
line_number = 0


def log(*messages):
    global line_number
    message = " ".join([str(item) for item in messages])
    if is_numerated:
        line_number += 1
        message = str(line_number) + '> ' + message
    cur_date = date.today().strftime('%Y-%m-%d')
    if write_to_file:
        try:
            f = open(cur_date, 'a')
            f.write(message + '\n')
            # f.writelines([(message)])
            f.close()
        except IOError as error:
            print("Log file error: %s" % error)
    print(message)
