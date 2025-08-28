import streamlit as st
import pandas as pd
from src.recommender import upsert_jobs_in_vectorstore, recommend

st.set_page_config(page_title="AI Job Recommender", layout="wide")

st.title("🔍 AI Job Recommender (FAISS + Gemini)")

tab1, tab2 = st.tabs(["📤 Upload Jobs Data", "💡 Get Recommendations"])

# ---------------------------
# Upload Jobs CSV & Store in FAISS
# ---------------------------
with tab1:
    st.header("Upload Job Postings CSV")
    uploaded_file = st.file_uploader("Upload CSV file with job data", type=["csv"])

    if uploaded_file:
        jobs_df = pd.read_csv(uploaded_file)

        st.write("Preview of uploaded jobs:")
        st.dataframe(jobs_df.head())

        if st.button("Store in FAISS Vector Store"):
            try:
                upsert_jobs_in_vectorstore(jobs_df)
                st.success("Jobs successfully stored in FAISS vector store!")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------------------------
# Get Job Recommendations
# ---------------------------
with tab2:
    st.header("Find Jobs Matching Your Skills")
    user_query = st.text_area("Describe the type of job you are looking for:", "")

    top_k = st.slider("Number of recommendations:", min_value=1, max_value=10, value=5)

    if st.button("Get Recommendations"):
        if not user_query.strip():
            st.warning("Please enter a job description or skills first.")
        else:
            try:
                recs = recommend(user_query, top_k=top_k)
                if recs:
                    for i, job in enumerate(recs, start=1):
                        st.subheader(f"{i}. {job['title']} - {job['company']}")
                        st.write(f"📍 Location: {job['location']}")
                        st.write(f"🔗 [Apply Here]({job['link']})")
                        with st.expander("📝 Job Description"):
                            st.write(job["description"])
                else:
                    st.info("No matching jobs found.")
            except Exception as e:
                st.error(f"Error: {e}")
