from os import walk

def file_names_in_sheets_directory():
    names = []
    for (dirpath, dirnames, filenames) in walk('sheets'):
        names += filenames
    return names

file_name = '2019-07-24_transaction_download.csv'
if file_name[-4:] == '.csv':
    file_name = file_name[:-4]
print(file_name)