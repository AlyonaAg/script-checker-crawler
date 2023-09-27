import csv

def write_to_csv(data):
    print('data:', data)

    with open('data.csv', 'a') as the_file:
        write = csv.writer(the_file)
        write.writerow(data)
