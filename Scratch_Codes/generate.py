import string
import random
import pandas as pd
from datetime import datetime, timedelta

letters = string.ascii_uppercase

lls = []
for n in range(0,15):
    lls.append(''.join(random.choice(letters) for i in range(3)) + "2866" + ''.join(random.choice(letters)))

print(lls)

lorry_tyre_locs = ['S1-L', 'S1-R', 'D1-L-IN', 'D1-L-OUT', 'D2-L-IN', 'D2-L-OUT', 'D1-R-IN', 'D1-R-OUT', 'D2-R-IN', 'D2-R-OUT']
trailer_tyre_locs = ['TA1-L-IN', 'TA1-L-OUT', 'TA2-L-IN', 'TA2-L-OUT', 'TA3-L-IN', 'TA3-L-OUT', 'TA4-L-IN', 'TA4-L-OUT', 'TA1-R-IN', 'TA1-R-OUT', 'TA2-R-IN', 'TA2-R-OUT', 'TA3-R-IN', 'TA3-R-OUT', 'TA4-R-IN', 'TA4-R-OUT']

emp_names = ['Ahmad', 'Sudin', 'Wong', 'Tan', 'Loo']

prod_ls = ['Tyre_A', 'Tyre_BB', 'Tyre_CCC']

dlist = []
ct = -1
for lorry in lls:
    ct += 1
    for i in range(0, 8):
        this_dt = datetime.now().date() - timedelta(days=i*300+random.randint(-60,60)+round(random.random()*10*ct))
        this_mileage = 130000 - (i * 12000 + round(random.random(), 3) * 1000)
        this_emp = emp_names[random.randint(0,4)]

        for loc in lorry_tyre_locs:
            dlist.append({'Date': this_dt, 'Activity': "Tyre Replace", 'Reason': "Worn Out", 'Employee_Name': this_emp, 'Tyre_Name': prod_ls[random.randint(0,2)], 'Tyre_Serial': ''.join(random.choice(letters)) + str(random.randint(180000, 200000)) + '-' + str(random.randint(10,99)), 'Vehicle_Number': lorry, 'Vehicle_Type': "Truck", 'Vehicle_Mileage': this_mileage, 'Tyre_Location': loc, 'Tyre_Size': "295/80R22.5"})

        for loc in trailer_tyre_locs:
            dlist.append({'Date': this_dt, 'Activity': "Tyre Replace", 'Reason': "Worn Out", 'Employee_Name': this_emp, 'Tyre_Name': prod_ls[random.randint(0,2)], 'Tyre_Serial': ''.join(random.choice(letters)) + str(random.randint(180000, 200000)) + '-' + str(random.randint(10,99)), 'Vehicle_Number': lorry, 'Vehicle_Type': "Trailer", 'Vehicle_Mileage': this_mileage, 'Tyre_Location': loc, 'Tyre_Size': "295/80R22.5"})

df = pd.DataFrame(dlist)
df.sort_values('Date', inplace=True)
df.to_csv("tyre_tracking_db.csv", index=False)
