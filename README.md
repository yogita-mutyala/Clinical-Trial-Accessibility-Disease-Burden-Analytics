# Clinical-Trial-Accessibility-Disease-Burden-Analytics
The project aims to analyze the accessibility of clinical trials across different disease areas in the United States and check whether clinical trial availability aligns with disease burden. 

## Data Sources 
1. ClinicalTrials.gov API link 
Provides structured data on clinical trials, including study conditions, locations, and recruitment status. 
Method: Data will be collected via API calls in Python and parsed from JSON responses. 
2. CDC Disease Prevalence Data link 
Contains datasets on disease prevalence and public health indicators across U.S. states. 
Method: Data will be accessed via downloadable CSV files or API endpoints and processed using pandas. 
3. U.S. State and Population Data link 
Provides population and geographic reference data for normalization and regional comparisons. 
Method: Data will be obtained in CSV format and used to standardize location-based analysis. 
## Data Integration Plan 
The data sources will be integrated based on common attributes such as disease/condition names and 
geographic regions. 
● Clinical trial data will provide information on the number and location of trials for each condition. 
● CDC data will provide disease prevalence metrics across states. 
● Census data will be used to normalize results. 
Data cleaning and normalization will be required to ensure consistency in naming conventions. This will help in  the comparison of trial availability and disease burden across regions and conditions. 
## Planned Analysis and Questions 
The project will perform exploratory and comparative analysis using Python. Key questions include: 
● Which disease categories have the highest number of clinical trials? 
● How does clinical trial availability vary across U.S. states? 
● Are regions with higher disease prevalence receiving proportional clinical trial attention? 
● Which diseases show the largest mismatch between prevalence and trial availability? 
## Expected Outcome 
The project aims to produce visualizations and insights that highlight disparities in clinical trial accessibility. 
These findings may reveal gaps in research coverage and help better understand how healthcare resources are distributed across disease areas and regions.
