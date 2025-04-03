import pandas as pd
import numpy as np

def clean_sales_data(input_file, output_file):
    # Read the CSV file with the first two rows as headers
    df = pd.read_csv(input_file, header=[0, 1])
    
    # Drop the empty "Order ID" column that has no header
    df = df.drop(columns=[col for col in df.columns if 'Order ID' in str(col)], errors='ignore')
    
    # Flatten the multi-index columns
    df.columns = ['_'.join(col).strip() for col in df.columns.values]
    
    # Identify the Order ID column (it's the first column without headers)
    # In your data, it's the first column that starts with 'CA-' or 'US-'
    order_id_col = df.columns[0]
    df = df.rename(columns={order_id_col: 'Order_ID'})
    
    # Melt the dataframe to long format
    id_vars = ['Order_ID']
    value_vars = [col for col in df.columns if col not in id_vars]
    
    melted_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, 
                       var_name='Segment_ShipMode', value_name='Amount')
    
    # Split Segment and Ship Mode
    melted_df[['Segment', 'Ship_Mode']] = melted_df['Segment_ShipMode'].str.split('_', n=1, expand=True)
    melted_df.drop('Segment_ShipMode', axis=1, inplace=True)
    
    # Clean segment names (remove 'Total')
    melted_df['Segment'] = melted_df['Segment'].str.replace('_Total', '')
    
    # For rows where Ship_Mode is NaN, set it to 'Total'
    melted_df['Ship_Mode'] = melted_df['Ship_Mode'].fillna('Total')
    
    # Convert Amount to numeric and drop NA
    melted_df['Amount'] = pd.to_numeric(melted_df['Amount'], errors='coerce')
    melted_df = melted_df.dropna(subset=['Amount'])
    
    # Remove rows with 0 amount
    melted_df = melted_df[melted_df['Amount'] != 0]
    
    # Reorder columns
    melted_df = melted_df[['Order_ID', 'Segment', 'Ship_Mode', 'Amount']]
    
    # Save to CSV
    melted_df.to_csv(output_file, index=False)
    
    return melted_df

# Example usage:
input_file = 'Ditry_Data_Sample.csv'
output_file = 'Cleaned_Sales_Data.csv'

try:
    cleaned_data = clean_sales_data(input_file, output_file)
    print(f"Data cleaned and saved to {output_file}")
    print(f"Total rows processed: {len(cleaned_data)}")
    print("Sample of cleaned data:")
    print(cleaned_data.head())
except Exception as e:
    print(f"Error occurred: {str(e)}")