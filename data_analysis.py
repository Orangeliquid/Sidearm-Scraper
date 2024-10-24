import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns


with open('Ohio_Dominican_University_Tables_Data_2023-24_Modified.json', 'r') as f:
    data = json.load(f)

# isolate starting key in data
top_key = list(data.keys())[0]
# access top category in json
json_top = data[top_key]
json_top_keys = list(json_top.keys())
for key, num in enumerate(json_top_keys):
    print(f"{num}: {key}")
top_key_choice = int(input("Enter the category number you desire: "))
print("\n")

# specify 1 of 5 categories - for instance "Individual"
subcategory_lvl = json_top[json_top_keys[top_key_choice]]
subcategory_lvl_keys = list(subcategory_lvl.keys())
for key, num in enumerate(subcategory_lvl_keys):
    print(f"{num}: {key}")
individual_lvl_choice = int(input("Enter the subcategory number you desire: "))
print("\n")

if top_key_choice == 0:
    next_lvl = subcategory_lvl[subcategory_lvl_keys[individual_lvl_choice]]
    next_lvl_keys = list(next_lvl.keys())
    for key, num in enumerate(next_lvl_keys):
        print(f"{num}: {key}")
    next_lvl_choice = int(input("Enter the next category number you desire: "))
    lowest_lvl = next_lvl[next_lvl_keys[next_lvl_choice]]
    # lowest_lvl_keys = list(lowest_lvl.keys())
else:
    lowest_lvl = subcategory_lvl[subcategory_lvl_keys[individual_lvl_choice]]
    # lowest_lvl_keys = list(lowest_lvl.keys())

# Convert the specific table into a DataFrame
df = pd.DataFrame(lowest_lvl)

# Transpose the DataFrame
if top_key_choice != 0:
    df = df.transpose()


# Check the structure after transposing
lowest_lvl_keys = list(df.keys())
for key, num in enumerate(lowest_lvl_keys):
    print(f"{num}: {key}")

y_choice = int(input("Enter the Y category number of your choice: "))

# drop Total Team and Opponents from df so the graphs aren't too large in values
if top_key_choice != 0:
    df = df.drop(index=["Team ", "Total", "Opponents"], errors='ignore')  # beware "Team " has a space after it


# Print the DataFrame to check the contents
print(df.head())
y_label = lowest_lvl_keys[y_choice]
print(y_label)
pref_column = df[y_label]

# Plot the FGM for each player
plt.figure(figsize=(10, 6))
sns.barplot(x=pref_column.index, y=pref_column.values, palette="Blues_d", hue=pref_column.index)
plt.xticks(rotation=90)  # Rotate player names for better visibility
plt.title(f"{y_label} per Entity")
plt.xlabel("Entity")
plt.ylabel(y_label)
plt.tight_layout()  # Adjust layout for better fit
plt.show()
