import streamlit as st
import datetime
import re

# ------------------ Config ------------------
STAFF_NAME = "Devadarsh P S"

# ------------------ Formatter ------------------
def extract_key_value(line):
    if ":" in line:
        k, v = line.split(":", 1)
        return k.strip(), v.strip()
    return None, line

def collect_column_widths(header_lines, task_blocks):
    max_key_len = 0
    for ln in header_lines:
        k, _ = extract_key_value(ln)
        if k:
            max_key_len = max(max_key_len, len(k))
    for block in task_blocks:
        for ln in block:
            k, _ = extract_key_value(ln)
            if k:
                max_key_len = max(max_key_len, len(k))
    return max_key_len

def reformat_block_lines(lines, pad_width):
    out = []
    for ln in lines:
        k, v = extract_key_value(ln)
        if k:
            out.append(f"{k.ljust(pad_width)} : {v}")
        else:
            out.append(ln.strip())
    return out

def renumber_task_header(header, num):
    m = re.match(r"^\s*Task\s*\d+", header)
    if m:
        return f"Task {num}"
    return header

def format_document_preserve_order(raw_text):
    lines = [ln.rstrip() for ln in raw_text.splitlines()]
    task_idx = [i for i, ln in enumerate(lines) if re.match(r"^\s*Task\s*\d+", ln)]
    if not task_idx:
        return raw_text
    header = lines[:task_idx[0]]
    tasks = []
    for i, idx in enumerate(task_idx):
        end = task_idx[i+1] if i+1 < len(task_idx) else len(lines)
        tasks.append(lines[idx:end])
    pad = collect_column_widths(header, tasks)
    formatted = []
    formatted += reformat_block_lines(header, pad)
    formatted.append("---------------------------------------")
    for i, block in enumerate(tasks, start=1):
        block[0] = renumber_task_header(block[0], i)
        formatted += reformat_block_lines(block, pad)
        formatted.append("---------------------------------------")
    return "\n".join(formatted).strip()

# ------------------ UI ------------------
st.set_page_config("Daily Work Report Generator", layout="wide")

st.title("🧾 Daily Work Report Generator ")
st.caption("Your daily work Report Generator.")

# Initialize session state
if "sessions" not in st.session_state:
    st.session_state.sessions = []

# Add Session Button
if st.button("➕ Add Session"):
    st.session_state.sessions.append({
        "branch": "Head Office",
        "checkin": "09:00",
        "checkout": "17:00",
        "tasks": []
    })

# List Sessions
for s_idx, session in enumerate(st.session_state.sessions):
    with st.expander(f"Session {s_idx+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        session["branch"] = c1.selectbox("Branch", ["Head Office", "Thevara"], key=f"branch{s_idx}", index=["Head Office", "Thevara"].index(session["branch"]))
        session["checkin"] = c2.time_input("Check-in Time", datetime.time(9, 0), key=f"checkin{s_idx}")
        session["checkout"] = c3.time_input("Check-out Time", datetime.time(17, 0), key=f"checkout{s_idx}")

        st.write("### Tasks")
        if st.button("Add Task", key=f"add_task_{s_idx}"):
            session["tasks"].append({
                "assigned_by": "Viswam Sir",
                "nature": "Regular Work",
                "progress": "Completed",
                "desc": "",
                "start": "09:00",
                "end": "17:00"
            })

        for t_idx, task in enumerate(session["tasks"]):
            with st.container():
                st.markdown(f"#### Task {t_idx+1}")
                c1, c2, c3 = st.columns(3)
                task["assigned_by"] = c1.selectbox("Assigned by", ["Viswam Sir", "Custom..."], key=f"assign{s_idx}_{t_idx}")
                task["nature"] = c2.selectbox("Nature", ["Regular Work", "Special Work"], key=f"nature{s_idx}_{t_idx}")
                task["progress"] = c3.selectbox("Progress", ["Completed", "In Progress", "Pending"], key=f"progress{s_idx}_{t_idx}")

                task["desc"] = st.text_area("Description", task["desc"], key=f"desc{s_idx}_{t_idx}")
                c4, c5 = st.columns(2)
                task["start"] = c4.time_input("Start Time", datetime.time(9, 0), key=f"start{s_idx}_{t_idx}")
                task["end"] = c5.time_input("End Time", datetime.time(17, 0), key=f"end{s_idx}_{t_idx}")

                if st.button("❌ Delete Task", key=f"del_task_{s_idx}_{t_idx}"):
                    session["tasks"].pop(t_idx)
                    st.experimental_rerun()

        if st.button("🗑️ Delete Session", key=f"del_session_{s_idx}"):
            st.session_state.sessions.pop(s_idx)
            st.experimental_rerun()

# Generate Report Button
if st.button("📄 Generate Report"):
    lines = []
    today = datetime.date.today().strftime("%d/%m/%Y")
    lines.append(f"Name of staff : {STAFF_NAME}")
    lines.append(f"Date :- {today}")
    lines.append("---------------------------------------")

    total_duration = datetime.timedelta()

    for s_idx, session in enumerate(st.session_state.sessions, start=1):
        lines.append(f"Check in time :- {session['checkin']}")
        for t_idx, task in enumerate(session["tasks"], start=1):
            lines.append(f"Task {t_idx}")
            lines.append(f"Work assigned by : {task['assigned_by']}")
            lines.append(f"Nature of work : {task['nature']}")
            lines.append(f"Description of work : {task['desc']}")
            start_str = str(task["start"])
            end_str = str(task["end"])
            lines.append(f"Duration and time spent on work:- {start_str}--{end_str}")
            lines.append(f"Progress : {task['progress']}")
            lines.append("Reason for incomplete :")
            lines.append("Remarks :")
            lines.append("---------------------------------------")

        lines.append(f"Office check out time : {session['checkout']}")
        lines.append("---------------------------------------")

    report_text = "\n".join(lines)
    formatted = format_document_preserve_order(report_text)
    st.session_state["report_text"] = formatted

if "report_text" in st.session_state:
    st.subheader("🪄 Formatted Preview")
    st.text_area("Preview", st.session_state["report_text"], height=400)

    # Download
    st.download_button(
        label="💾 Download as TXT",
        data=st.session_state["report_text"],
        file_name=f"WorkReport_{datetime.date.today()}.txt",
        mime="text/plain"
    )

