def main():
    filename = 'results_2/logs/run.log'
    is_next = False
    with open(filename) as f:
        for l in f:
            if is_next:
                print(l.split(' ')[-1].strip(' \n'))
                is_next = False
            if 'Test result' in l:
                is_next = True

main()
