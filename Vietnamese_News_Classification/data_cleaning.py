import pandas as pd

df = pd.read_csv('data_set.csv')

df = df.dropna()
df['link'] = df['link'].apply(lambda x: x if x.startswith("https://") else f"https://vietnamnet.vn{x}")
df = df.drop_duplicates()

df.to_csv('data_set.csv',index=False)

category_counts = df['category'].value_counts()

def main():
    print("Category Counts:")
    print(category_counts)

if __name__ == '__main__':
    main()