import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from budget_logic import analyze_expenses
from llm_agent import budget_ai_agent, chat_with_data, generate_savings_plan

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Analytics Dashboard", page_icon="💰", layout="wide")

st.title("💰 Smart AI Budget Analytics")
st.markdown("Upload your bank statement or expense sheet (CSV) to get instant AI-powered insights.")

# Check if API key is set
if not os.environ.get("GROQ_API_KEY"):
    st.warning("⚠️ GROQ_API_KEY environment variable not set. AI features will show an error until the key is configured.")
    st.info("To set the API key, create a .env file in the project root with: `GROQ_API_KEY=your_api_key_here` or set the environment variable directly.")

with st.sidebar:
    st.header("Data Upload")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    st.info("Make sure your CSV has columns like 'Category' and 'Amount'.")

if uploaded_file:
    try:
        raw_df = pd.read_csv(uploaded_file)
        
        analysis_result = analyze_expenses(raw_df)
        
        cleaned_df = analysis_result["df"]
        total_spend = analysis_result["total"]
        top_cat = analysis_result["top_category"]
        cat_summary = analysis_result["category_summary"]
        llm_text = analysis_result["llm_text"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spending", f"₹{total_spend:,.2f}")
        col2.metric("Top Category", top_cat)
        col3.metric("Transactions", len(cleaned_df))

        st.divider()

        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Spending by Category")
            st.bar_chart(cat_summary, color="#FF4B4B")
            
        with c2:
            st.subheader("Raw Data")
            st.dataframe(cleaned_df[["date", "category", "amount", "description"]] if "date" in cleaned_df.columns else cleaned_df[["category", "amount", "description"]], 
                         use_container_width=True, height=300)

        st.divider()
        st.header("🤖 AI Financial Advisor")
        
        tab1, tab2, tab3 = st.tabs(["📊 Advisor Report", "💬 Chat with Budget", "💰 Savings Plan"])
        
        with tab1:
            st.caption("Get a professional analysis of your overall spending health.")
            if st.button("Generate Full Report", key="btn_report"):
                advice_stream = budget_ai_agent(llm_text)
                st.write_stream(advice_stream)

        with tab2:
            st.caption("Ask specific questions like 'How much did I spend on Food?' or 'Where can I cut costs?'.")
            user_question = st.text_input("Ask your question:", key="chat_input")
            if st.button("Ask AI", key="btn_chat"):
                if user_question:
                    answer_stream = chat_with_data(llm_text, user_question)
                    st.write_stream(answer_stream)
                else:
                    st.warning("Please enter a question first.")

        with tab3:
            st.caption("Generate a personalized savings strategy based on 50/30/20 rule.")
            if st.button("Create Savings Strategy", key="btn_savings"):
                plan_stream = generate_savings_plan(llm_text)
                st.write_stream(plan_stream)

    except ValueError as ve:
        st.error(f"Data Error: {ve}")
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
else:
    st.info(" Upload keywords: ``category``, ``amount``. Don't worry about standardizing, our AI logic cleans it for you!")
