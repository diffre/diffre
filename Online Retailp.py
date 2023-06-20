import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('Mall_Customers.csv')

# Define a function to assign customer groups based on their characteristics
def assign_customer_group(row):
    if row['Age'] < 30 and row['Annual Income (k$)'] < 40:
        return 'Group 1'
    elif row['Age'] >= 30 and row['Annual Income (k$)'] >= 40:
        return 'Group 2'
    else:
        return 'Group 3'

# Apply the function to create the 'customer_group' column
df['customer_group'] = df.apply(assign_customer_group, axis=1)

# Calculate the 'satisfaction' column using the formula
df['satisfaction'] = 0.4 * df['Age'] + 0.3 * df['Annual Income (k$)'] + 0.3 * df['Spending Score (1-100)']

# Continue with your data analysis or operations on the DataFrame
# ...

# Example: Access the 'satisfaction' column for Group 1 customers
group1 = df[df['customer_group'] == 'Group 1']['satisfaction']

# Descriptive Statistics
summary_statistics = df.describe()  # Calculate summary statistics (mean, median, etc.)
print(summary_statistics)

# Hypothesis Testing
# Example: t-test to compare customer satisfaction levels between different customer groups
group2 = df[df['customer_group'] == 'Group 2']['satisfaction']
t_statistic, p_value = ttest_ind(group1, group2)
print("T-statistic:", t_statistic)
print("P-value:", p_value)

# Regression Analysis
# Example: Linear regression to explore the relationship between demographic factors and purchasing decisions

# Perform linear regression
X = df[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']]
y = df['satisfaction']

# Create data
x = [1, 2, 3, 4, 5]
y = [10, 12, 8, 15, 11]

# Plot scatter plot
plt.scatter(x, y)

# Add labels and title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Scatter Plot')

# Display the chart
plt.show()
# Create data
x = [1, 2, 3, 4, 5]
y = [10, 12, 8, 15, 11]

# Plot line chart
plt.plot(x, y)

# Add labels and title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Line Chart')

# Display the chart
plt.show()
import matplotlib.pyplot as plt

# Create data
categories = ['Category 1', 'Category 2', 'Category 3']
values = [10, 15, 8]

# Plot bar chart
plt.bar(categories, values)

# Add labels and title
plt.xlabel('Categories')
plt.ylabel('Values')
plt.title('Bar Chart')

# Display the chart
plt.show()

# Create a linear regression model
linear_model = LinearRegression()

# Fit the model to the data
linear_model.fit(X, y)

# Get the coefficients and intercept
coefficients = linear_model.coef_
intercept = linear_model.intercept_

# Print the coefficients and intercept
print("Coefficients:", coefficients)
print("Intercept:", intercept)

# Cluster Analysis
# Example: K-means clustering to identify customer segments with similar buying patterns
X_cluster = df[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']]  # Features used for clustering
kmeans = KMeans(n_clusters=3)  # Number of clusters to identify
kmeans.fit(X_cluster)
labels = kmeans.labels_
df['cluster_label'] = labels
print(df['cluster_label'].value_counts())

# Data Visualization
# Example: Bar chart to visualize customer satisfaction by customer group
grouped_df = df.groupby('customer_group')['satisfaction'].mean()
grouped_df.plot(kind='bar', xlabel='Customer Group', ylabel='Customer Satisfaction')
plt.show()
