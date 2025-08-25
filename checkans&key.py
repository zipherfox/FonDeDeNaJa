import pandas as pd

checked = []

def compare_csv(first_file: str, second_file: str):
    df_first = pd.read_csv(first_file, header=0, on_bad_lines="skip", )
    df_second = pd.read_csv(second_file, header=0, on_bad_lines="skip")
    correct = 1
    wrong = 0

    while True:
        # Access all lines where first contains same with second csv
        if df_first[df_first.apply(tuple, 1).isin(df_second.apply(tuple,1))]:
            checked.append(correct)
    
        # Use Tilde to access all lines where first doesn't contain second csv
        if df_first[~df_first.apply(tuple, 1).isin(df_second.apply(tuple,1))]:
            checked.append(wrong)
        
        if df_second.empty:


if __name__ == '__main__':
    compare_csv("first.csv", "second.csv")

questionScore = {'score': 1}
questionScore['score'] = checked

df = pd.DataFrame(questionScore)

csv_file_path = 'checkedresults.csv'

df.to_csv(csv_file_path, index=False)

print(f'CSV file &quot;{csv_file_path}&quot; has been created successfully.')