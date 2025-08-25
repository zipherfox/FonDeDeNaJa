import pandas as pd

global checked, result, weight
checked=0
result=()
weight = (1, 2)

def compare_csv(first_file: str, second_file: str):
    student = pd.read_csv(first_file, header=0, on_bad_lines="skip", )
    key = pd.read_csv(second_file, header=0, on_bad_lines="skip")
    
    # Access all lines where first contains same with second csv
    result = student.apply(tuple, 1).isin(key.apply(tuple,1))
    result.replace({False: 0, True: 1}, inplace=True)
    for i in range(0,len(result)):
        checked+=result[i]
    result.append(checked)

if __name__ == '__main__':
    compare_csv("student.csv", "key.csv")

df = pd.DataFrame(result)

csv_file_path = 'checkedresults.csv'

df.to_csv(csv_file_path, index=False)

print(f'CSV file &quot;{csv_file_path}&quot; has been created successfully.')