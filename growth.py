import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="💿 Data sweeper", layout='wide')
st.title("💿 Data sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# Corrected file type to 'csv' instead of 'cvs'
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display info about the file
        st.write(f"*File Name:* {file.name}")
        st.write(f"*File Size:* {file.size/1024:.2f} KB")  # Format the file size for better readability

        # Show 5 rows of the dataframe
        st.write("🔍Preview the Head of the Dataframe")
        st.dataframe(df.head())
        
        # Options for data cleaning
        st.subheader("🛠️Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values have been Filled!")
     
        # Choose Specific Columns to Keep or Convert 
        st.subheader("🎯Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Create Some Visualizations
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            # Only select numeric columns for visualization
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Limit the data to the first two columns
                df_for_chart = df[numeric_cols].iloc[:, :2].dropna()  # Remove NaN values
                if df_for_chart.empty:
                    st.error("No data available for visualization after cleaning!")
                else:
                    st.bar_chart(df_for_chart)  # Plot the data
            else:
                st.error("No numeric columns available for visualization!")

        # Convert the File -> CSV to Excel
        st.subheader("🔄Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:",["CSV","Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)  # Correct method name: to_csv
                file_name = file.name.replace(file_ext, ".csv")  # Correct extension
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                try:
                    # Try using openpyxl as engine
                    df.to_excel(buffer, index=False, engine='openpyxl')
                except Exception as e:
                    st.error(f"Error writing Excel file: {e}")
                    # Fallback to XlsxWriter if openpyxl fails
                    df.to_excel(buffer, index=False, engine='xlsxwriter')
                file_name = file.name.replace(file_ext, ".xlsx")  # Correct extension
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                filename=file_name,
                mime=mime_type
            )    

st.success("🎉 All files processed!")

st.markdown("Made ❤️ Saba Muhammad Riaz 💻✨")
