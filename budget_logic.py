import pandas as pd
import numpy as np

def clean_data(df):
    df.columns = [c.lower().strip() for c in df.columns]
    
    col_mapping = {
        'cost': 'amount',
        'price': 'amount',
        'value': 'amount',
        'type': 'category',
        'desc': 'description',
        'item': 'description'
    }
    df = df.rename(columns=col_mapping)
    
    if 'amount' not in df.columns:
        raise ValueError("Could not find an 'amount' column. Please name one column 'Amount' or 'Price'.")
    if 'category' not in df.columns:
        df['category'] = 'Uncategorized'
        
    def clean_currency(x):
        if isinstance(x, str):
            clean_str = x.replace('₹', '').replace('$', '').replace(',', '').strip()
            try:
                return float(clean_str)
            except ValueError:
                return 0.0
        return x

    df['amount'] = df['amount'].apply(clean_currency)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    
    if 'description' not in df.columns:
        df['description'] = 'Unknown Transaction'
        
    return df

def analyze_expenses(df):
    cleaned_df = clean_data(df)
    
    total_spending = cleaned_df["amount"].sum()
    category_summary = cleaned_df.groupby("category")["amount"].sum().sort_values(ascending=False)
    
    if not category_summary.empty:
        top_category = category_summary.index[0]
        top_cat_amount = category_summary.iloc[0]
    else:
        top_category = "None"
        top_cat_amount = 0

    llm_summary = f"Total Spending: ₹{total_spending:,.2f}\n"
    llm_summary += f"Top Category: {top_category} (₹{top_cat_amount:,.2f})\n\n"
    llm_summary += "Category Breakdown:\n"
    for cat, amt in category_summary.items():
        llm_summary += f"- {cat}: ₹{amt:,.2f}\n"

    return {
        "df": cleaned_df,
        "total": total_spending,
        "category_summary": category_summary,
        "top_category": top_category,
        "llm_text": llm_summary
    }
