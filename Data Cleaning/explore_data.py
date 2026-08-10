import pandas as pd

# Load CSV dataset
df = pd.read_csv(".tickets_clean.csv")

print("=" * 50)
print("Dataset Shape")
print("=" * 50)
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 Records:")
print(df.head())

print("\nTicket Type Distribution:")
print(df["type"].value_counts())

print("\nTicket Priority Distribution:")
print(df["priority"].value_counts())

"""print("\nTicket Status:")
print(df["Ticket Status"].value_counts())"""


print("\nMissing Values:")
print(df.isnull().sum())

corr_matrix = df.corr(numeric_only=True)
print(corr_matrix)

"""print(df['Ticket Channel'].value_counts(normalize=True) * 100)
"""

print(df['type'].value_counts(normalize=True) * 100)

print(df['priority'].value_counts(normalize=True) * 100)

"""print(df['Product Purchased'].value_counts(normalize=True) * 100)

print(df['Customer Gender'].value_counts(normalize=True) * 100)

print((df['Customer Age']
 .value_counts(normalize=True)
 .sort_index()
 * 100))

print(df.groupby('Ticket Status')[[
    'Resolution',
    'Time to Resolution',
    'Customer Satisfaction Rating'
]].apply(lambda x: x.isna().sum())
)
"""

