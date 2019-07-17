import csv
import pandas as pd

csv_data = input("Please input the name of the csv file(without .csv): ")
# csv_data = "2019-06-15_transaction_download"

with open(csv_data+'.csv') as csvfile:
    csvreader = csv.reader(csvfile) 
    fields = next(csvreader) 
    Jess_amount = 0
    Pete_amount = 0
    for row in csvreader:
        if row[6] != '' and row[3] == "9246":
            Pete_amount += float(row[6])
        if row[6] != '' and row[3] == "0717":
            Jess_amount += float(row[6])
        if row[7] != '' and row[3] == "9246":
            Pete_amount -= float(row[7])
        if row[7] != '' and row[3] == "0717":
            Jess_amount -= float(row[7])
print("Pete's total is: "+str(round(Pete_amount,2)))
print("Jess' total is: "+str(round(Jess_amount,2)))

data = pd.read_csv (csv_data+'.csv') 
data1 = data[[' Card No.',' Category',' Debit']]
groupby_sum1 = data1.groupby([' Card No.',' Category']).sum() 
groupby_sum1.rename(columns={' Card No.':'Name'},inplace=True)
print (str(groupby_sum1))

