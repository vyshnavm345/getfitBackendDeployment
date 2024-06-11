import csv

# Initialize an empty list to store tuples
countries = []

# Open the CSV file
with open('countries.csv', mode='r', encoding='utf-8-sig') as file:
    # Create a CSV reader object
    csv_reader = csv.DictReader(file)
    
    # Iterate over each row in the CSV file
    for row in csv_reader:
        # Append a tuple of country name and alpha-3 code to the list
        countries.append((row['country'], row['alpha-3']))
