#!/usr/bin/env python
# coding: utf-8

# ###Working With FS CORS data

# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as g
import warnings
warnings.filterwarnings("ignore")


# In[2]:


# List of Nutrients - Load all CSVs, set a consistent 'district' column,
# rename the last (value) column to the requested descriptive name, and drop duplicates by district
import glob
import os

csv_files = [
    'nutrients/Calcium.csv', 'nutrients/Foliate.csv', 'nutrients/Iron.csv', 'nutrients/Kilocaleries.csv',
    'nutrients/Proteins.csv', 'nutrients/Riboflavin.csv', 'nutrients/Thiamin.csv', 'nutrients/VitaminA.csv', 'nutrients/VitaminB12.csv',
    'nutrients/VitaminB6.csv', 'nutrients/VitaminC.csv', 'nutrients/Zinc.csv',
]

# Units (as provided) and pretty display names where needed
units = {
    'Calcium': 'mg',
    'Foliate': 'mcg',      # assuming Foliate -> Folate
    'Niacin': 'mg',        # not present in csv_files; kept for completeness
    'Proteins': 'mg',
    'Kilocaleries': 'kcal',
    'Iron': 'mg',
    'Riboflavin': 'mg',
    'Thiamin': 'mg',
    'VitaminA': 'mcg',
    'VitaminB12': 'mcg',
    'VitaminB6': 'mg',
    'VitaminC': 'mg',
    'Zinc': 'mg',
}

# Friendly display names (for nicer column titles)
display_name = {
    'Calcium': 'Calcium',
    'Foliate': 'Folate',
    'Proteins': 'Proteins',
    'Kilocaleries': 'Kilocaleries',
    'Iron': 'Iron',
    'Riboflavin': 'Riboflavin',
    'Thiamin': 'Thiamin',
    'VitaminA': 'Vitamin A',
    'VitaminB12': 'Vitamin B12',
    'VitaminB6': 'Vitamin B6',
    'VitaminC': 'Vitamin C',
    'Zinc': 'Zinc',
}

nutrient_dfs = {}
missing_files = []
for file in csv_files:
    if not os.path.exists(file):
        missing_files.append(file)
        continue
    df = pd.read_csv(file)
    # Ensure we have at least two columns (district and value)
    if df.shape[1] < 2:
        nutrient_dfs[file.replace('.csv','')] = df
        continue
    # Robustly identify the district column: prefer columns with 'name' or 'district' in the header, else use column index 1
    district_col = None
    for col in df.columns:
        lname = str(col).lower()
        if 'district' in lname or 'name' in lname:
            district_col = col
            break
    if district_col is None and len(df.columns) >= 2:
        district_col = df.columns[1]
    # Rename the district column to 'district'
    if district_col is not None:
        df = df.rename(columns={district_col: 'district'})
    # Build last-column display name based on filename base
    base = file.replace('.csv','')
    pretty = display_name.get(base, base)
    unit = units.get(base, '')
    # Compose the requested column name
    value_col_new = f'Average Consumption adequacy of {pretty} ({unit})' if unit else f'Average Consumption adequacy of {pretty}'
    # Rename the last column (whatever it currently is) to the composed name
    last_col = df.columns[-1]
    # If last_col is already 'district' (rare), try to find the numeric/value column instead
    if last_col == 'district' and df.shape[1] >= 2:
        last_col = df.columns[-1]  # fallback - keeps being last
    df = df.rename(columns={last_col: value_col_new})
    # Drop duplicates by district if the district column exists
    if 'district' in df.columns:
        df = df.drop_duplicates(subset=['district']).reset_index(drop=True)
    nutrient_dfs[base] = df

# Report missing files (if any) and show a sample head for verification
print('Missing files skipped:', missing_files)
if 'Calcium' in nutrient_dfs:
    nutrient_dfs['Calcium'].head()


# In[3]:


#Obtaining dataframes
for df_name, df in nutrient_dfs.items():
    print(f"DataFrame for {df_name}:")
    print(df.head())


# In[4]:


# Merge safe: reduce each dataframe to ['district', '<nutrient_value>'] where the value column is detected robustly
valid_dfs = {k: v for k, v in nutrient_dfs.items() if isinstance(v, pd.DataFrame) and 'district' in v.columns}
print('DataFrames found for merge:', list(valid_dfs.keys()))

if not valid_dfs:
    print('No valid DataFrames with a "district" column available to merge.')
else:
    cleaned = {}
    for name, df in valid_dfs.items():
        # columns except 'district'
        other_cols = [c for c in df.columns if c != 'district']
        if not other_cols:
            print(f'Skipping {name}: no value column found')
            continue
        # Prefer a column containing the 'Average Consumption adequacy' phrase
        val_col = None
        for c in other_cols:
            if 'Average Consumption adequacy' in str(c):
                val_col = c
                break
        # Fallback to numeric columns
        if val_col is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_cols = [c for c in numeric_cols if c != 'district']
            if numeric_cols:
                val_col = numeric_cols[0]
        # Final fallback: last non-district column
        if val_col is None:
            val_col = other_cols[-1]
        # Compose a clean, unique column name for this nutrient
        pretty = display_name.get(name, name)
        unit = units.get(name, '')
        new_col = f'Average Consumption adequacy of {pretty} ({unit})' if unit else f'Average Consumption adequacy of {pretty}'
        # Select and rename
        cleaned_df = df[['district', val_col]].copy()
        cleaned_df = cleaned_df.rename(columns={val_col: new_col})
        # Drop duplicates by district
        cleaned_df = cleaned_df.drop_duplicates(subset=['district']).reset_index(drop=True)
        cleaned[name] = cleaned_df
    # Now merge all cleaned dfs on 'district'
    from functools import reduce
    dfs_to_merge = list(cleaned.values())
    if not dfs_to_merge:
        print('No cleaned DataFrames to merge')
    else:
        merged_nutrients = reduce(lambda left, right: pd.merge(left, right, on='district', how='outer'), dfs_to_merge)
        merged_nutrients = merged_nutrients.sort_values('district').reset_index(drop=True)
        nutrient_dfs['merged_by_district'] = merged_nutrients
        print('Merged shape:', merged_nutrients.shape)
        merged_nutrients.head()


# In[5]:


merged_nutrients


# Average Consumption adequacy = (average in take of Nutrients / recommended intake of Nutrients )* 100

# In[6]:


merged_nutrients.isna().sum()


# In[7]:


merged_nutrients.to_csv('merged_nutrients.csv', index=False)


# In[8]:


merged_nutrients.duplicated().sum()


# In[9]:


merged_nutrients.rename(columns={'Average Consumption adequacy of Kilocaleries (kcal)': 'Consumption adequacy of Kilocaleries (kcal)'}, inplace=True)


# In[10]:


merged_nutrients


# In[11]:


merged_nutrients.columns


# In[12]:


merged_nutrients.describe()


# In[ ]:

merged_nutrients.rename(columns={'Average Consumption adequacy of Kilocaleries (kcal)': 'Consumption adequacy of Kilocaleries (kcal)'}, inplace=True)

## Average  Consumption adequacy of Nutrients



merged_nutrients

merged_nutrients.columns

### Exploring Districts with the lowest adequacy in various nutrients in Uganda

### Calcium


nutrient = "Average Consumption adequacy of Calcium (mg)"
bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

### Folate

nutrient =    "Average Consumption adequacy of Folate (mcg)"
bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Iron

nutrient ="Average Consumption adequacy of Iron (mg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Kilocaleries

nutrient =  "Consumption adequacy of Kilocaleries (kcal)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Proteins

nutrient =  "Average Consumption adequacy of Proteins (mg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()
# Riboflavin

nutrient ="Average Consumption adequacy of Riboflavin (mg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Thiamin

nutrient = "Average Consumption adequacy of Thiamin (mg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Vitamin A

nutrient = "Average Consumption adequacy of Vitamin A (mcg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

## Vitamin B12

nutrient ="Average Consumption adequacy of Vitamin B12 (mcg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Vitamin B6

nutrient ="Average Consumption adequacy of Vitamin B6 (mg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(

    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Vitamin C

nutrient ="Average Consumption adequacy of Vitamin C (mg)"

bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()

# Zinc

nutrient = "Average Consumption adequacy of Zinc (mg)"
bottom5 = merged_nutrients.nsmallest(5, nutrient)
bottom5["Group"] = "Bottom 5"

# Horizontal bar chart
fig = px.bar(
    bottom5,
    x=nutrient,
    y="district",
    color="Group",
    text=nutrient,
    orientation="h",
     color_discrete_map={
         "Bottom 5": "red"
          }
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title=f"Bottom 5 Districts by {nutrient}",
    xaxis_title="Adequacy",
    yaxis_title="District",
    yaxis=dict(categoryorder="total ascending")
)

fig.show()



fig = px.scatter(merged_nutrients,
                 x='Consumption adequacy of Kilocaleries (kcal)',
                 y="Average Consumption adequacy of Iron (mg)",
                 title="Hidden Hunger: Calories vs Iron Adequacy",
                 hover_data='district')
fig.show()





# ### Index Vulneablilty Analysis
# 

# In[26]:


from functools import reduce
import pandas as pd

files = [
    ("Index datasets/composite-vulnerability.csv", "Composite Vulnerability Index"),
    ("Index datasets/health-system-vulnerabil.csv", "Health System Vulnerability Index"),
    ("Index datasets/mean-adequacy-ratio-inde.csv", "Mean Adequacy Ratio Index"),
    ("Index datasets/per-capita-food-consumpt.csv", "Per Capita Food Consumption Index"),
    ("Index datasets/vulnerability-to-climate.csv", "Vulnerability to Climate Change Index"),
]

dfs = []
for path, name in files:
    df = pd.read_csv(path)
    df.columns = ["Category", name]
    dfs.append(df)

merged_index = reduce(lambda left, right: pd.merge(left, right, on="Category", how="outer"), dfs)
merged_index = merged_index.rename(columns={'Category': 'Region'})
merged_index.head()
merged_index.to_csv("merged_index.csv", index=False)


# In[27]:


merged_index.head()


# ### Communicating  Composite Vulnerability   
# Composite Vulnerability Index – An overall combined measure of vulnerability across multiple dimensions (health, food, climate, etc.). A higher value suggests higher vulnerability.

# In[34]:


composite=merged_index[['Region','Composite Vulnerability Index']].sort_values(by='Composite Vulnerability Index', ascending=False).drop_duplicates(subset=['Region']).reset_index(drop=True)
composite.head()


# In[35]:


# Bar Composite Vulnerability by Category
fig = px.bar(
    composite,
    x="Region",  # Regions (Acholi, Buganda, etc.)
    y="Composite Vulnerability Index",  # Value to plot
    title="Composite Vulnerability Index by Region",
    color="Composite Vulnerability Index",  # Color scale based on value
    #color_continuous_scale="Reds"
)

# Rotate x-axis labels for readability
fig.update_layout(xaxis_tickangle=-45,
                  coloraxis_colorbar=dict(title="Vulnerability Index"))


# ### Composite Vulnerability Index by Region  
# 
# The **Composite Vulnerability Index (CVI)** is the average of four dimensions:  
# - **Health System Vulnerability**  
# - **Mean Adequacy Ratio (nutrition adequacy)**  
# - **Per Capita Food Consumption**  
# - **Vulnerability to Climate Change**  
# 
# This provides a single measure (0 = low, 1 = high) to compare regions.  
# 
# > **Insight:** Acholi, Lango, and Busoga are the most vulnerable regions, while Kampala and Elgon are the least.  
# > This suggests interventions should target the high-risk regions first to strengthen resilience.  
# 

# ### Healthy System Vulnerability
# 

# In[36]:


health=merged_index[['Region','Health System Vulnerability Index']].sort_values(by='Health System Vulnerability Index', ascending=False).drop_duplicates(subset=['Region']).reset_index(drop=True)
health.head()


# In[37]:


# Plot the health vulnerability dataframe.
# Use the numeric 'Health System Vulnerability Index' as the marker size
# (the previous size="pop" raised an error because 'pop' doesn't exist in `health`)
fig = px.scatter(
	health,
	x="Health System Vulnerability Index",
	y="Region",
	size="Health System Vulnerability Index",
	color="Health System Vulnerability Index",
	title="Health System Vulnerability Index by Region",
	labels={"Category": "Region", "Health System Vulnerability Index": "Health System Vulnerability Index"}
)
# Order categories by value for clearer display
fig.update_layout(yaxis={'categoryorder': 'total ascending'})
fig.show()


# ### Health System Vulnerability Index
# 
# The **Health System Vulnerability Index** measures a region’s susceptibility to health system challenges.  
# **Scale:** 0 = low vulnerability, 1 = high vulnerability.
# 
# > **Insight:**  
# > **Lango** is the most vulnerable region, while **Kampala** is the least.  
# > Prioritize interventions in high-risk areas like **Lango** to improve resilience.
# 

# ### Food Security

# In[38]:


Food_security=merged_index[['Region','Mean Adequacy Ratio Index','Per Capita Food Consumption Index']].drop_duplicates(subset=['Region']).reset_index(drop=True)
Food_security.head()


# In[39]:


# Create scatter plot using the Food_security dataframe and correct column names
fig = px.scatter(
    Food_security,
    x='Per Capita Food Consumption Index',
    y='Mean Adequacy Ratio Index',
    color='Region',
    hover_data=['Region'],
    labels={
        'Per Capita Food Consumption Index': 'Per Capita Food Consumption (index)',
        'Mean Adequacy Ratio Index': 'Mean Adequacy Ratio (index)',
        'Category': 'Region'
    },
    title='Nutrition Adequacy vs Food Consumption by Region'
)
fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=2, color='DarkSlateGrey')))
fig.show()


# ### Nutrition Adequacy vs Food Consumption by Region  
# 
# This chart compares **per capita food consumption** with the **mean adequacy ratio of nutrients** across regions.  
# - Regions higher on the chart have **better nutrient adequacy**, even if food consumption is low.  
# - Regions further right show **higher food consumption**, though this does not always guarantee adequate nutrition.  
# 
# > **Insight:**  
# > Some regions consume more food but still have low nutrient adequacy, highlighting the need for **diverse diets and nutrition-focused interventions**.  
# 

# ## Climate Change Vulnerability index

# In[40]:


composite=merged_index[['Region','Vulnerability to Climate Change Index']].sort_values(by='Vulnerability to Climate Change Index', ascending=False).drop_duplicates(subset=['Region']).reset_index(drop=True)
composite.head()


# In[41]:


# Bar Composite Vulnerability by Category
fig = px.bar(
    composite,
    x="Region",  # Regions (Acholi, Buganda, etc.)
    y="Vulnerability to Climate Change Index",  # Value to plot
    title="Vulnerability to Climate Change Index by Region",
    color="Vulnerability to Climate Change Index",  # Color scale based on value
    #color_continuous_scale="Reds"
)

# Rotate x-axis labels for readability
fig.update_layout(xaxis_tickangle=-45,
                  coloraxis_colorbar=dict(title="Vulnerability Index"))


# ### Vulnerability to Climate Change Index by Region  
# 
# This chart shows how different regions are exposed to the risks of **climate change**, with values ranging from 0 (low vulnerability) to 1 (high vulnerability).  
# 
# - **Kigezi, Busoga, and Ankole** show the **highest vulnerability**, meaning they face the greatest climate risks.  
# - **Kampala and Elgon** are the **least vulnerable**, but resilience strategies remain important.  
# 
# > **Insight:**  
# > Regions like **Kigezi and Busoga** need urgent climate adaptation measures, while lower-risk regions should focus on sustaining their resilience.  
# 
