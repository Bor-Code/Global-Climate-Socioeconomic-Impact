# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

# Set visualization style and figure size
plt.style.use('seaborn-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
sns.set_palette("viridis")
warnings.filterwarnings('ignore')

# For reproducibility
np.random.seed(42)

# Load the datasets for all years
df_2015 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2015.csv')
df_2016 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2016.csv')
df_2017 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2017.csv')
df_2018 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2018.csv')
df_2019 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2019.csv')
df_2020 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2020.csv')
df_2021 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2021.csv')
df_2022 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2022.csv')
df_2023 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2023.csv')
df_2024 = pd.read_csv('/kaggle/input/world-happiness-report-2015-2024/2024.csv')

# Display basic information about the datasets
years = list(range(2015, 2025))
datasets = [df_2015, df_2016, df_2017, df_2018, df_2019, df_2020, df_2021, df_2022, df_2023, df_2024]

for year, df in zip(years, datasets):
    print(f"{year} Dataset Shape: {df.shape}")

# Let's look at the first few rows of selected datasets to understand their structure
print("Sample data from 2015:")
display(df_2015.head(2))

print("\nSample data from 2019:")
display(df_2019.head(2))

print("\nSample data from 2024:")
display(df_2024.head(2))

# Display column information for each dataset
for year, df in zip(years, datasets):
    print(f"{year} Dataset Columns:")
    print(df.columns.tolist())
    print(f"Number of missing values: {df.isnull().sum().sum()}\n")

# Display statistical summaries for selected datasets (2015, 2020, 2024)
print("2015 Statistical Summary:")
display(df_2015.describe())

print("\n2020 Statistical Summary:")
display(df_2020.describe())

print("\n2024 Statistical Summary:")
display(df_2024.describe())

# Create standardized column mappings for each dataset
# We'll create new dataframes with standardized column names

# For 2015
df_2015_std = df_2015.copy()
df_2015_std['Year'] = 2015
df_2015_std = df_2015_std.rename(columns={
    'Country': 'Country',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness Score': 'Happiness_Score',
    'Economy (GDP per Capita)': 'GDP_per_Capita',
    'Family': 'Social_Support',
    'Health (Life Expectancy)': 'Life_Expectancy',
    'Freedom': 'Freedom',
    'Trust (Government Corruption)': 'Corruption',
    'Generosity': 'Generosity',
    'Dystopia Residual': 'Dystopia_Residual'
})

# For 2016
df_2016_std = df_2016.copy()
df_2016_std['Year'] = 2016
df_2016_std = df_2016_std.rename(columns={
    'Country': 'Country',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness Score': 'Happiness_Score',
    'Economy (GDP per Capita)': 'GDP_per_Capita',
    'Family': 'Social_Support',
    'Health (Life Expectancy)': 'Life_Expectancy',
    'Freedom': 'Freedom',
    'Trust (Government Corruption)': 'Corruption',
    'Generosity': 'Generosity',
    'Dystopia Residual': 'Dystopia_Residual'
})

# For 2017
df_2017_std = df_2017.copy()
df_2017_std['Year'] = 2017
df_2017_std = df_2017_std.rename(columns={
    'Country': 'Country',
    'Happiness.Rank': 'Happiness_Rank',
    'Happiness.Score': 'Happiness_Score',
    'Economy..GDP.per.Capita.': 'GDP_per_Capita',
    'Family': 'Social_Support',
    'Health..Life.Expectancy.': 'Life_Expectancy',
    'Freedom': 'Freedom',
    'Trust..Government.Corruption.': 'Corruption',
    'Generosity': 'Generosity',
    'Dystopia.Residual': 'Dystopia_Residual'
})

# For 2018
df_2018_std = df_2018.copy()
df_2018_std['Year'] = 2018
df_2018_std = df_2018_std.rename(columns={
    'Country or region': 'Country',
    'Overall rank': 'Happiness_Rank',
    'Score': 'Happiness_Score',
    'GDP per capita': 'GDP_per_Capita',
    'Social support': 'Social_Support',
    'Healthy life expectancy': 'Life_Expectancy',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Corruption',
    'Generosity': 'Generosity'
})

# For 2019
df_2019_std = df_2019.copy()
df_2019_std['Year'] = 2019
df_2019_std = df_2019_std.rename(columns={
    'Country or region': 'Country',
    'Overall rank': 'Happiness_Rank',
    'Score': 'Happiness_Score',
    'GDP per capita': 'GDP_per_Capita',
    'Social support': 'Social_Support',
    'Healthy life expectancy': 'Life_Expectancy',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Corruption',
    'Generosity': 'Generosity'
})

# For 2020
df_2020_std = df_2020.copy()
df_2020_std['Year'] = 2020
df_2020_std = df_2020_std.rename(columns={
    'Country name': 'Country',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness score': 'Happiness_Score',
    'Economy (GDP per Capita)\t': 'GDP_per_Capita',
    'Social support': 'Social_Support',
    'Healthy life expectancy': 'Life_Expectancy',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Corruption',
    'Generosity': 'Generosity'
})

# For 2021
df_2021_std = df_2021.copy()
df_2021_std['Year'] = 2021
df_2021_std = df_2021_std.rename(columns={
    'Country name': 'Country',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness score': 'Happiness_Score',
    'Economy (GDP per Capita)\t': 'GDP_per_Capita',
    'Social support': 'Social_Support',
    'Healthy life expectancy': 'Life_Expectancy',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Corruption',
    'Generosity': 'Generosity'
})

# For 2022
df_2022_std = df_2022.copy()
df_2022_std['Year'] = 2022
df_2022_std = df_2022_std.rename(columns={
    'Country name': 'Country',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness score': 'Happiness_Score',
    'Economy (GDP per Capita)\t': 'GDP_per_Capita',
    'Social support': 'Social_Support',
    'Healthy life expectancy': 'Life_Expectancy',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Corruption',
    'Generosity': 'Generosity'
})

# For 2023
df_2023_std = df_2023.copy()
df_2023_std['Year'] = 2023
df_2023_std = df_2023_std.rename(columns={
    'Country name': 'Country',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness score': 'Happiness_Score',
    'Economy (GDP per Capita)\t': 'GDP_per_Capita',
    'Social support': 'Social_Support',
    'Healthy life expectancy': 'Life_Expectancy',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Corruption',
    'Generosity': 'Generosity'
})

# For 2024
df_2024_std = df_2024.copy()
df_2024_std['Year'] = 2024
df_2024_std = df_2024_std.rename(columns={
    'Country name': 'Country',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness score': 'Happiness_Score',
    'Economy (GDP per Capita)\t': 'GDP_per_Capita',
    'Social support': 'Social_Support',
    'Healthy life expectancy': 'Life_Expectancy',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Corruption',
    'Generosity': 'Generosity'
})

print("Column standardization completed for all datasets.")

# Check for missing values in each standardized dataset
standardized_dfs = [df_2015_std, df_2016_std, df_2017_std, df_2018_std, df_2019_std,
                    df_2020_std, df_2021_std, df_2022_std, df_2023_std, df_2024_std]

for year, df in zip(years, standardized_dfs):
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"Missing values in {year} dataset:")
        print(missing[missing > 0])
    else:
        print(f"No missing values in {year} dataset.")

# Fill missing values with the median of the respective column
for year, df in zip(years, standardized_dfs):
    for column in df.columns:
        if df[column].isnull().sum() > 0:
            median_value = df[column].median()
            df[column].fillna(median_value, inplace=True)
            print(f"Filled missing values in {year} dataset, column '{column}' with median: {median_value:.4f}")

# Verify no missing values remain
for year, df in zip(years, standardized_dfs):
    if df.isnull().sum().sum() > 0:
        print(f"Warning: {year} dataset still has missing values!")
    else:
        pass  # All missing values have been handled

# Select common columns across all datasets
common_columns = ['Country', 'Happiness_Rank', 'Happiness_Score', 'GDP_per_Capita', 
                 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 
                 'Generosity', 'Year']

# Create a combined dataset
combined_datasets = []
for df in standardized_dfs:
    combined_datasets.append(df[common_columns])

df_combined = pd.concat(combined_datasets, ignore_index=True)

print(f"Combined dataset shape: {df_combined.shape}")
display(df_combined.head())

# Verify number of countries per year in the combined dataset
countries_per_year = df_combined.groupby('Year')['Country'].count()
print("Number of countries by year:")
display(countries_per_year)

# Examine the unique countries in the dataset
total_unique_countries = df_combined['Country'].nunique()
print(f"Total unique countries across all years: {total_unique_countries}")

# Create a mapping for inconsistent country names
country_name_mapping = {
    'United States': 'United States of America',
    'Congo (Kinshasa)': 'Democratic Republic of the Congo',
    'Congo (Brazzaville)': 'Republic of Congo',
    'North Cyprus': 'Northern Cyprus',
    'Hong Kong S.A.R. of China': 'Hong Kong',
    'Hong Kong S.A.R., China': 'Hong Kong',
    'Taiwan Province of China': 'Taiwan',
    'Palestinian Territories': 'Palestine'
    # Add more mappings as needed
}

# Apply the mapping to standardize country names
df_combined['Country'] = df_combined['Country'].replace(country_name_mapping)

# Check unique countries after harmonization
harmonized_unique_countries = df_combined['Country'].nunique()
print(f"Unique countries after harmonization: {harmonized_unique_countries}")

# Create boxplots for key variables to identify outliers
plt.figure(figsize=(15, 10))

# Select numerical columns for outlier detection
numerical_cols = ['Happiness_Score', 'GDP_per_Capita', 'Social_Support', 
                  'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']

# Plot boxplots for each numerical column
for i, col in enumerate(numerical_cols, 1):
    plt.subplot(2, 4, i)
    sns.boxplot(y=df_combined[col])
    plt.title(f'Boxplot of {col}')
    plt.tight_layout()

plt.suptitle('Outlier Analysis for Key Variables', fontsize=16, y=1.05)
plt.tight_layout()
plt.show()

# Calculate average happiness score by year
yearly_avg = df_combined.groupby('Year')['Happiness_Score'].mean().reset_index()

plt.figure(figsize=(12, 7))
sns.lineplot(x='Year', y='Happiness_Score', data=yearly_avg, marker='o', linewidth=2.5, color='#1f77b4')
plt.title('Global Average Happiness Score (2015-2024)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Average Happiness Score', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(yearly_avg['Year'])

# Add value labels
for x, y in zip(yearly_avg['Year'], yearly_avg['Happiness_Score']):
    plt.text(x, y + 0.02, f'{y:.3f}', ha='center', fontsize=10)

# Add vertical line for COVID-19 pandemic onset
plt.axvline(x=2020, color='red', linestyle='--', alpha=0.7, label='COVID-19 Pandemic')
plt.legend()
    
plt.tight_layout()
plt.show()

# Get data for 2024
df_2024_data = df_combined[df_combined['Year'] == 2024].copy()

# Get top 10 and bottom 10 countries by happiness score
top10 = df_2024_data.nsmallest(10, 'Happiness_Rank')
bottom10 = df_2024_data.nlargest(10, 'Happiness_Rank')

# Create side by side bar plots
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Top 10 countries
sns.barplot(ax=axes[0], y='Country', x='Happiness_Score', data=top10.sort_values('Happiness_Score', ascending=False), 
            palette='viridis')
axes[0].set_title('Top 10 Happiest Countries (2024)', fontsize=16)
axes[0].set_xlabel('Happiness Score', fontsize=12)
axes[0].set_ylabel('Country', fontsize=12)
axes[0].bar_label(axes[0].containers[0], fmt='%.2f', padding=3)

# Bottom 10 countries
sns.barplot(ax=axes[1], y='Country', x='Happiness_Score', data=bottom10.sort_values('Happiness_Score'), 
            palette='viridis')
axes[1].set_title('Bottom 10 Least Happy Countries (2024)', fontsize=16)
axes[1].set_xlabel('Happiness Score', fontsize=12)
axes[1].set_ylabel('', fontsize=12)
axes[1].bar_label(axes[1].containers[0], fmt='%.2f', padding=3)

plt.tight_layout()
plt.show()

# Get the top 5 countries from the most recent year (2024)
top5_countries = top10.nsmallest(5, 'Happiness_Rank')['Country'].tolist()

# Create a dataframe with data for these countries across all years
top5_data = df_combined[df_combined['Country'].isin(top5_countries)]

# Plot the evolution of their rankings over time
plt.figure(figsize=(14, 8))

# We need to reverse the y-axis since rank 1 is the top position
g = sns.lineplot(x='Year', y='Happiness_Rank', hue='Country', data=top5_data, 
              palette='viridis', linewidth=2.5, marker='o', markersize=10)

# Invert y-axis so rank 1 is at the top
plt.gca().invert_yaxis()
plt.title('Evolution of Top 5 Countries\'s Happiness Rankings (2015-2024)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Happiness Rank', fontsize=14)
plt.xticks(years)
plt.grid(True, linestyle='--', alpha=0.7)

# Set y-axis to show only ranks 1-15
plt.ylim(15, 1)

# Add value labels for rankings
for country in top5_countries:
    country_data = top5_data[top5_data['Country'] == country]
    for x, y in zip(country_data['Year'], country_data['Happiness_Rank']):
        plt.text(x, y, f'{int(y)}', ha='center', va='bottom', fontsize=9)

plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Calculate correlation matrix for 2024 data
correlation = df_2024_data[['Happiness_Score', 'GDP_per_Capita', 'Social_Support', 
                      'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']].corr()

# Create heatmap
plt.figure(figsize=(12, 10))
mask = np.triu(correlation)
sns.heatmap(correlation, annot=True, fmt=".2f", cmap='viridis', mask=mask,
            linewidths=.5, cbar_kws={"shrink": .8})
plt.title('Correlation Between Happiness Factors (2024)', fontsize=16)
plt.tight_layout()
plt.show()

# Calculate correlation between happiness score and each factor for each year
correlation_data = []

for year in years:
    year_data = df_combined[df_combined['Year'] == year]
    for factor in ['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']:
        corr = year_data['Happiness_Score'].corr(year_data[factor])
        correlation_data.append({
            'Year': year,
            'Factor': factor,
            'Correlation': corr
        })

corr_df = pd.DataFrame(correlation_data)

# Plot the evolution of correlation coefficients over time
plt.figure(figsize=(14, 8))
for factor in ['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']:
    factor_data = corr_df[corr_df['Factor'] == factor]
    plt.plot(factor_data['Year'], factor_data['Correlation'], marker='o', linewidth=2, label=factor)

plt.title('Evolution of Correlation Coefficients with Happiness Score (2015-2024)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Correlation Coefficient', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(years)
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
plt.legend(title='Factor', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Create scatterplots for each factor vs Happiness Score (2024 data)
factors = ['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.flatten()

for i, factor in enumerate(factors):
    sns.regplot(ax=axes[i], x=factor, y='Happiness_Score', data=df_2024_data, 
                scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    axes[i].set_title(f'{factor} vs. Happiness Score', fontsize=14)
    axes[i].set_xlabel(factor, fontsize=12)
    axes[i].set_ylabel('Happiness Score', fontsize=12)
    
    # Add correlation coefficient
    corr = df_2024_data[factor].corr(df_2024_data['Happiness_Score'])
    axes[i].annotate(f'r = {corr:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', 
                     fontsize=12, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="b", lw=1))

plt.suptitle('Relationship Between Factors and Happiness Score (2024)', fontsize=18, y=1.02)
plt.tight_layout()
plt.show()

plt.figure(figsize=(16, 8))
sns.violinplot(x='Year', y='Happiness_Score', data=df_combined, palette='viridis', inner='quartile')
plt.title('Distribution of Happiness Scores by Year', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Happiness Score', fontsize=14)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Add mean value as a point on each violin plot
means = df_combined.groupby('Year')['Happiness_Score'].mean()
plt.plot(range(len(years)), means.values, 'ro', markersize=8)

plt.tight_layout()
plt.show()

# Define pre-COVID and post-COVID periods
pre_covid = df_combined[df_combined['Year'] < 2020]
during_covid = df_combined[(df_combined['Year'] >= 2020) & (df_combined['Year'] <= 2022)]
post_covid = df_combined[df_combined['Year'] > 2022]

# Calculate average values for each period
factors_to_analyze = ['Happiness_Score', 'GDP_per_Capita', 'Social_Support', 
                     'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']

pre_covid_avg = pre_covid[factors_to_analyze].mean()
during_covid_avg = during_covid[factors_to_analyze].mean()
post_covid_avg = post_covid[factors_to_analyze].mean()

# Create a dataframe for plotting
covid_impact_df = pd.DataFrame({
    'Pre-COVID (2015-2019)': pre_covid_avg,
    'During COVID (2020-2022)': during_covid_avg,
    'Post-COVID (2023-2024)': post_covid_avg
}).reset_index().rename(columns={'index': 'Factor'})

# Melt the dataframe for easier plotting
covid_impact_melted = covid_impact_df.melt(id_vars='Factor', var_name='Period', value_name='Average Value')

# Create the plot
plt.figure(figsize=(16, 10))
sns.barplot(x='Factor', y='Average Value', hue='Period', data=covid_impact_melted, palette='viridis')
plt.title('Impact of COVID-19 on Happiness Factors', fontsize=16)
plt.xlabel('Factor', fontsize=14)
plt.ylabel('Average Value', fontsize=14)
plt.xticks(rotation=45)
plt.legend(title='Period', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Use 2015 data which has region information
df_regions = df_2015[['Country', 'Region']].copy()

# Merge with the 2024 data
df_2024_regions = pd.merge(df_2024_data, df_regions, on='Country', how='left')

# Calculate average happiness by region for 2024
region_happiness = df_2024_regions.groupby('Region')['Happiness_Score'].agg(['mean', 'count', 'min', 'max']).reset_index()
region_happiness = region_happiness.sort_values('mean', ascending=False)

# Create a bar plot of average happiness by region
plt.figure(figsize=(14, 8))
bar_plot = sns.barplot(x='Region', y='mean', data=region_happiness, palette='viridis')
plt.title('Average Happiness Score by Region (2024)', fontsize=16)
plt.xlabel('Region', fontsize=14)
plt.ylabel('Average Happiness Score', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Add the number of countries per region on top of each bar
for i, row in enumerate(region_happiness.itertuples()):
    bar_plot.text(i, row.mean + 0.1, f'n={row.count}', ha='center')

plt.tight_layout()
plt.show()

# Select some major countries from different regions
major_countries = ['United States', 'United Kingdom', 'France', 'Germany', 'Japan', 
                   'China', 'India', 'Brazil', 'Russia', 'South Africa']

# Filter data for these countries
major_countries_data = df_combined[df_combined['Country'].isin(major_countries)]

# Plot happiness trends
plt.figure(figsize=(14, 8))
sns.lineplot(x='Year', y='Happiness_Score', hue='Country', data=major_countries_data, 
             palette='tab10', linewidth=2.5, markers=True)
plt.title('Happiness Score Trends for Major Countries (2015-2024)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Happiness Score', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(years)
plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Perform ANOVA to test if happiness scores differ significantly across years
from scipy.stats import f_oneway

# Get happiness scores for each year
happiness_by_year = [df_combined[df_combined['Year'] == year]['Happiness_Score'] for year in years]

# Perform ANOVA
f_stat, p_value = f_oneway(*happiness_by_year)

print(f"ANOVA Results for Happiness Scores Across Years (2015-2024):")
print(f"F-statistic: {f_stat:.4f}")
print(f"p-value: {p_value:.4f}")
print(f"Statistically significant difference: {p_value < 0.05}")

# Perform t-test to compare pre-COVID and post-COVID happiness scores
from scipy.stats import ttest_ind

# Pre-COVID (2015-2019) vs Post-COVID (2023-2024)
pre_covid_scores = pre_covid['Happiness_Score']
post_covid_scores = post_covid['Happiness_Score']

# Perform t-test
t_stat, p_value = ttest_ind(pre_covid_scores, post_covid_scores, equal_var=False)

print(f"Independent t-test Results for Pre-COVID vs Post-COVID Happiness:")
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.4f}")
print(f"Statistically significant difference: {p_value < 0.05}")
print(f"Pre-COVID mean: {pre_covid_scores.mean():.4f}")
print(f"Post-COVID mean: {post_covid_scores.mean():.4f}")

# Pivot the correlation data for better visualization
corr_pivot = corr_df.pivot(index='Factor', columns='Year', values='Correlation')

# Plot correlation heatmap
plt.figure(figsize=(16, 8))
sns.heatmap(corr_pivot, annot=True, fmt='.2f', cmap='viridis')
plt.title('Correlation Between Factors and Happiness Score by Year (2015-2024)', fontsize=16)
plt.tight_layout()
plt.show()

# Prepare data for regression analysis (using 2024 data)
X = df_2024_data[['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']]
y = df_2024_data['Happiness_Score']

# Add constant for the intercept
import statsmodels.api as sm
X_with_const = sm.add_constant(X)

# Fit the regression model
model = sm.OLS(y, X_with_const).fit()

# Display the results
print(model.summary())

# Define time periods
periods = {
    'Early (2015-2017)': df_combined[(df_combined['Year'] >= 2015) & (df_combined['Year'] <= 2017)],
    'Pre-COVID (2018-2019)': df_combined[(df_combined['Year'] >= 2018) & (df_combined['Year'] <= 2019)],
    'COVID (2020-2022)': df_combined[(df_combined['Year'] >= 2020) & (df_combined['Year'] <= 2022)],
    'Recent (2023-2024)': df_combined[(df_combined['Year'] >= 2023) & (df_combined['Year'] <= 2024)]
}

# Store model results
model_results = []

# Run regression for each period
for period_name, period_data in periods.items():
    X = period_data[['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']]
    y = period_data['Happiness_Score']
    
    # Add constant
    X_with_const = sm.add_constant(X)
    
    # Fit model
    model = sm.OLS(y, X_with_const).fit()
    
    # Extract coefficients and p-values
    for var in X.columns:
        model_results.append({
            'Period': period_name,
            'Factor': var,
            'Coefficient': model.params[var],
            'P-value': model.pvalues[var],
            'Significant': model.pvalues[var] < 0.05
        })
    
    # Add R-squared
    model_results.append({
        'Period': period_name,
        'Factor': 'R-squared',
        'Coefficient': model.rsquared,
        'P-value': None,
        'Significant': None
    })

# Create dataframe of results
model_comparison_df = pd.DataFrame(model_results)

# Display results
pivot_table = model_comparison_df.pivot_table(index='Factor', columns='Period', values='Coefficient')
display(pivot_table)

# Visualize coefficients across periods
factors_only = model_comparison_df[model_comparison_df['Factor'] != 'R-squared']

plt.figure(figsize=(16, 10))
bar_width = 0.2
positions = np.arange(len(factors_only['Factor'].unique()))

for i, period in enumerate(periods.keys()):
    period_data = factors_only[factors_only['Period'] == period]
    plt.bar(positions + i*bar_width, period_data['Coefficient'], 
            width=bar_width, label=period, alpha=0.7)

plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
plt.xticks(positions + bar_width*1.5, factors_only['Factor'].unique(), rotation=45)
plt.title('Regression Coefficients Across Time Periods', fontsize=16)
plt.xlabel('Factor', fontsize=14)
plt.ylabel('Coefficient Value', fontsize=14)
plt.legend(title='Time Period')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# We'll use the most recent data (2024) for our predictive modeling
X = df_2024_data[['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']]
y = df_2024_data['Happiness_Score']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Linear Regression Model
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)

# Make predictions
y_pred_lr = lr_model.predict(X_test_scaled)

# Evaluate the model
mse_lr = mean_squared_error(y_test, y_pred_lr)
r2_lr = r2_score(y_test, y_pred_lr)

print("Linear Regression Results:")
print(f"Mean Squared Error: {mse_lr:.4f}")
print(f"R² Score: {r2_lr:.4f}")
print(f"RMSE: {np.sqrt(mse_lr):.4f}")

# Random Forest Model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# Make predictions
y_pred_rf = rf_model.predict(X_test_scaled)

# Evaluate the model
mse_rf = mean_squared_error(y_test, y_pred_rf)
r2_rf = r2_score(y_test, y_pred_rf)

print("\nRandom Forest Results:")
print(f"Mean Squared Error: {mse_rf:.4f}")
print(f"R² Score: {r2_rf:.4f}")
print(f"RMSE: {np.sqrt(mse_rf):.4f}")

# Compare actual vs predicted values
results_df = pd.DataFrame({
    'Actual': y_test,
    'Linear Regression': y_pred_lr,
    'Random Forest': y_pred_rf
}).reset_index(drop=True)

# Plot the comparison
plt.figure(figsize=(12, 8))

plt.scatter(range(len(results_df)), results_df['Actual'], color='blue', label='Actual', s=100, alpha=0.7)
plt.scatter(range(len(results_df)), results_df['Linear Regression'], color='red', marker='x', label='Linear Regression', s=100)
plt.scatter(range(len(results_df)), results_df['Random Forest'], color='green', marker='^', label='Random Forest', s=100)

plt.title('Actual vs. Predicted Happiness Scores (2024)', fontsize=16)
plt.xlabel('Country Index', fontsize=12)
plt.ylabel('Happiness Score', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Get feature importances from the Random Forest model
feature_importance = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

# Plot feature importances
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance, palette='viridis')
plt.title('Feature Importance for Predicting Happiness (Random Forest)', fontsize=16)
plt.xlabel('Importance', fontsize=12)
plt.ylabel('Feature', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Train on pre-COVID data, test on post-COVID data
X_train_temporal = pre_covid[['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']]
y_train_temporal = pre_covid['Happiness_Score']

X_test_temporal = post_covid[['GDP_per_Capita', 'Social_Support', 'Life_Expectancy', 'Freedom', 'Corruption', 'Generosity']]
y_test_temporal = post_covid['Happiness_Score']

# Scale features
scaler_temporal = StandardScaler()
X_train_temporal_scaled = scaler_temporal.fit_transform(X_train_temporal)
X_test_temporal_scaled = scaler_temporal.transform(X_test_temporal)

# Train models
temporal_lr = LinearRegression()
temporal_lr.fit(X_train_temporal_scaled, y_train_temporal)

temporal_rf = RandomForestRegressor(n_estimators=100, random_state=42)
temporal_rf.fit(X_train_temporal_scaled, y_train_temporal)

# Make predictions
y_pred_temporal_lr = temporal_lr.predict(X_test_temporal_scaled)
y_pred_temporal_rf = temporal_rf.predict(X_test_temporal_scaled)

# Calculate metrics
lr_r2_temporal = r2_score(y_test_temporal, y_pred_temporal_lr)
rf_r2_temporal = r2_score(y_test_temporal, y_pred_temporal_rf)

print("Cross-Temporal Prediction Results (Pre-COVID → Post-COVID):")
print(f"Linear Regression R²: {lr_r2_temporal:.4f}")
print(f"Random Forest R²: {rf_r2_temporal:.4f}")