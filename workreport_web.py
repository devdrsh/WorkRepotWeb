import streamlit as st
import datetime
import re
import os
from io import StringIO
from PIL import Image
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ---------------------- CONFIGURATION ----------------------
st.set_page_config(page_title="MB Report", page_icon="MB.png", layout="wide")

# Load login credentials from config.yaml
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Setup authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# ---------------------- LOGIN ----------------------
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.image("Mblogo.png", width=140)
    st.sidebar.write(f"👤 Logged in as: **{name}**")

    st.title("📘 MB Report - Daily Work Report Generator")

    # ---------------------- DEPARTMENT & STAFF ----------------------
    st.header("Staff & Department Information")
    department = st.selectbox(
        "Department",
        ["Mathematics", "Chemistry", "Physics", "Biology", "Computer Science", "Hindi", "English", "Social Science", "Commerce"]
    )

    hods = {
        "Mathematics": "Arjun Sir",
        "Chemistry": "Agnal Sir",
        "Physics": "Viswam Sir",
        "Biology": "Vishak Sir",
        "Computer Science": "Deepak Sir",
        "Hindi": "Ebin Sir",
        "English": "Ebin Sir",
        "Social Science": "Agnal Sir",
        "Commerce": "Arjun Sir"
    }

    hod_name = hods.get(department, "HOD")

    staff_name = st.text_input("Name of Staff")
    date = st.date_input("Date", datetime.date.today())
    day_name = date.strftime("%A")

    st.markdown("---")

    # ---------------------- TASK SECTION ----------------------
    num_tasks = st.number_input("Number of Tasks", min_value=1, max_value=15, value=1)
    tasks = []
    total_duration = datetime.timedelta()

    for i in range(int(num_tasks)):
        st.subheader(f"Task {i+1}")
        nature = st.text_input(f"Nature of work (Task {i+1})", value="Regular Work")
        desc = st.text_area(f"Description (Task {i+1})")
        start = st.time_input(f"Start time (Task {i+1})", key=f"start{i}")
        end = st.time_input(f"End time (Task {i+1})", key=f"end{i}")
        progress = st.selectbox(f"Progress (Task {i+1})", ["Completed", "Incomplete"], key=f"prog{i}")

        duration = (
            datetime.datetime.combine(datetime.date.today(), end)
            - datetime.datetime.combine(datetime.date.today(), start)
        )
        tasks.append({
            "nature": nature,
            "desc": desc,
            "start": start.strftime("%H:%M"),
            "end": end.strftime("%H:%M"),
            "duration": str(duration)[:-3],
            "progress": progress
        })
        total_duration += duration

    total_hours_str = f"{int(total_duration.total_seconds()//3600)} hours {int((total_duration.total_seconds()%3600)//60)} min"

    st.markdown("---")

    # ---------------------- REPORT GENERATION ----------------------
    if st.button("📝 Generate Report"):
        output = StringIO()
        output.write(f"Department      : {department}\n")
        output.write(f"HOD             : {hod_name}\n")
        output.write(f"Name of Staff   : {staff_name}\n")
        output.write(f"Date - Day      : {date.strftime('%d/%m/%Y')} - {day_name}\n\n")

        for i, task in enumerate(tasks, start=1):
            output.write(f"Task {i}\n")
            output.write(f"Nature of work       : {task['nature']}\n")
            output.write(f"Description of work  : {task['desc']}\n")
            output.write(f"Duration and time    : {task['start']} - {task['end']} ({task['duration']})\n")
            output.write(f"Progress             : {task['progress']}\n")
            output.write("----------------------------------------\n")

        output.write(f"\nTotal Work Duration  : {total_hours_str}\n")

        report_text = output.getvalue()

        # --- Display Preview ---
        st.subheader("📄 Preview:")
        st.text_area("", report_text, height=400)

        # --- Save Report Locally ---
        if not os.path.exists("Reports"):
            os.makedirs("Reports")
        filename = f"Reports/{staff_name}_{date}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)

        st.success(f"✅ Report saved as {filename}")

        # --- Download & Copy ---
        st.download_button("⬇️ Download Report", report_text, file_name=f"{staff_name}_{date}.txt")
        st.code(report_text, language='text')

elif authentication_status is False:
    st.error("Incorrect username or password")
elif authentication_status is None:
    st.warning("Please log in to access the app")
