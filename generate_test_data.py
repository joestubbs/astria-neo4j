import random 
import os 


# update
#rows = 100000
#file_name = 'import/test_data_100k.csv'

rows = 500000
file_name = 'import/test_data_500k.csv'

#rows = 10000000
#file_name = 'import/test_data_10M.csv'

with open(file_name, 'w') as f:
    # write header
    f.write("row_id:ID,property_1,property_2:int\n")
    # write data
    for i in range(1, rows+1):
        row_id = i
        p1 = f"prp_{i}"
        p2 = random.randint(0, i)
        row = f"{row_id},{p1},{p2}\n"
        f.write(row)
