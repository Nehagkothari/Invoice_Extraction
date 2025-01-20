import pymssql
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Function to retrieve data from Azure SQL
def fetch_from_azure_sql():
    try:
        conn = pymssql.connect(
            server="piosqlserverbd.database.windows.net",
            user="pio-admin",
            password="Poctest123#",
            database="PIOSqlDB"
        )
        query = "SELECT * FROM Invoices"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function for saving changes to the database
def update_database(updated_rows):
    try:
        conn = pymssql.connect(
            server="piosqlserverbd.database.windows.net",
            user="pio-admin",
            password="Poctest123#",
            database="PIOSqlDB"
        )
        cursor = conn.cursor()

        for _, row in updated_rows.iterrows():
            update_query = """
            UPDATE Invoices
            SET ApprovalStatus = %s
            WHERE EmployeeID = %s
            """
            cursor.execute(update_query, (row["ApprovalStatus"], row["EmployeeID"]))
        
        conn.commit()
        conn.close()
        return "Updated are successfully saved!."
    except Exception as e:
        return f"Error saving data: {e}"

#  Streamlit
st.title("Admin Panel for Approval Status Updates, Table 'Invoices'")

# Upload data
data = fetch_from_azure_sql()

if data is not None:
    st.write("Data uploaded successfully from Azure SQL.")
    all_categories = data["ApprovalStatus"].unique()  
    selected_categories = st.multiselect(
        "Filer by ApprovalStatus",
        options=all_categories,
        default=all_categories,  
        help="Choose one or more statuses."
    )

    # Data Filtering
    filtered_df = data[data["ApprovalStatus"].isin(selected_categories)]

    column_order = [ "EmployeeID","Category", "Date", "Place", "InvoiceNumber", "Amount", "ApprovalStatus",  "ServiceOpted"]
    filtered_df=filtered_df[column_order]
    # Table with AgGrid
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    

    # Style for approval status column
    gb.configure_column(
        "ApprovalStatus",  
        cellStyle={"backgroundColor": "#c1f3ff", "color": "black"},  # colour of the Approval column
        editable=True,  # Allow adits
        cellEditor="agSelectCellEditor",  # 
        cellEditorParams={"values": ["Pending", "Approved", "Rejected"]}  # Options to choose
    )

    gb.configure_default_column(
        autoSizeColumns=True, wrapHeaderText=True)
    grid_options = gb.build()
    # Show the table
    grid_response = AgGrid(
        filtered_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        editable=True,
        height=520,
        width=1000
    )

    # Updated data
    updated_data = grid_response["data"]
    updated_df = pd.DataFrame(updated_data)

    # Button to save all updates
    if st.button("Save updates!"):
        status_message = update_database(updated_df)
        st.success(status_message)
else:
    st.error("Failed to load data from database.")
