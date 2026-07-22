import os
import uuid
import hashlib
import base64
from io import BytesIO
from datetime import date

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="School Management System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:

    st.error(
        "❌ Supabase credentials नहीं मिले। "
        "कृपया .env file check करें।"
    )

    st.code(
        """
SUPABASE_URL=https://YOUR-PROJECT-ID.supabase.co
SUPABASE_KEY=YOUR-SUPABASE-ANON-KEY
        """
    )

    st.stop()


# =========================================================
# SUPABASE CONNECTION
# =========================================================

try:

    supabase: Client = create_client(
        SUPABASE_URL="https://uxsgnyakxvbslsxuujup.supabase.co/rest/v1/",
        SUPABASE_KEY="sb_publishable_sGzpFNfmc6-pxd66T_Lguw_ziOQtCpB"
    )

except Exception as e:

    st.error(
        f"Supabase Connection Error: {e}"
    )

    st.stop()


# =========================================================
# DARK BLACK THEME
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #000000;
        color: #ffffff;
    }

    [data-testid="stSidebar"] {
        background-color: #050505;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, label, span {
        color: #eeeeee !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #444444 !important;
    }

    [data-baseweb="select"] > div {
        background-color: #111111 !important;
        color: white !important;
    }

    .stButton button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }

    .stButton button:hover {
        background-color: #1d4ed8;
    }

    [data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 15px;
    }

    .school-card {
        background: #111111;
        border: 1px solid #333333;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if "admission_no" not in st.session_state:
    st.session_state.admission_no = ""


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def logout():

    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.username = ""
    st.session_state.admission_no = ""

    st.rerun()


def get_grade(percentage):

    if percentage >= 90:
        return "A+"

    elif percentage >= 80:
        return "A"

    elif percentage >= 70:
        return "B+"

    elif percentage >= 60:
        return "B"

    elif percentage >= 50:
        return "C+"

    elif percentage >= 40:
        return "C"

    else:
        return "F"


def create_receipt_pdf(receipt, school):

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    school_name = (
        school.get(
            "school_name",
            "SCHOOL MANAGEMENT SYSTEM"
        )
        if school
        else "SCHOOL MANAGEMENT SYSTEM"
    )

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        width / 2,
        height - 60,
        school_name
    )

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawCentredString(
        width / 2,
        height - 90,
        "FEE PAYMENT RECEIPT"
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    y = height - 140

    lines = [

        f"Receipt No: {receipt['receipt_no']}",

        f"Student Name: {receipt['student_name']}",

        f"Admission No: {receipt['admission_no']}",

        f"Class: {receipt['class_name']}",

        f"Fee Type: {receipt['fee_type']}",

        f"Total Fee: Rs. {receipt['total_fee']}",

        f"Paid Amount: Rs. {receipt['paid_amount']}",

        f"Due Amount: Rs. {receipt['due_amount']}",

        f"Payment Method: {receipt['payment_method']}",

        f"Payment Date: {receipt['payment_date']}"

    ]

    for line in lines:

        pdf.drawString(
            70,
            y,
            line
        )

        y -= 30

    pdf.line(
        70,
        y - 10,
        width - 70,
        y - 10
    )

    pdf.drawString(
        70,
        y - 50,
        "Authorized Signature"
    )

    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    st.title(
        "🏫 School Management System"
    )

    st.markdown(
        """
        <div class="school-card">

        <h2>Welcome to School Portal</h2>

        <p>
        Admin और Student के लिए Secure Management System
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "🔐 Admin Login",
            "👨‍🎓 Student Login",
            "📝 Student Register"
        ]
    )


    # =====================================================
    # ADMIN LOGIN
    # =====================================================

    with tab1:

        st.subheader(
            "🔐 Admin Login"
        )

        username = st.text_input(
            "Username",
            key="admin_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="admin_password"
        )

        if st.button(
            "🔐 Login as Admin",
            use_container_width=True
        ):

            if not username or not password:

                st.error(
                    "Username और Password required हैं."
                )

            else:

                try:

                    result = (
                        supabase
                        .table("admins")
                        .select("*")
                        .eq(
                            "username",
                            username.strip()
                        )
                        .eq(
                            "password",
                            password.strip()
                        )
                        .execute()
                    )

                    if result.data:

                        st.session_state.logged_in = True

                        st.session_state.role = "admin"

                        st.session_state.username = (
                            username.strip()
                        )

                        st.success(
                            "Admin Login Successful!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Invalid Username or Password."
                        )

                except Exception as e:

                    st.error(
                        f"Login Error: {e}"
                    )


    # =====================================================
    # STUDENT LOGIN
    # =====================================================

    with tab2:

        st.subheader(
            "👨‍🎓 Student Login"
        )

        admission_no = st.text_input(
            "Admission Number",
            key="student_login_admission"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="student_login_password"
        )

        if st.button(
            "👨‍🎓 Login as Student",
            use_container_width=True
        ):

            if not admission_no or not password:

                st.error(
                    "Admission Number और Password required हैं."
                )

            else:

                try:

                    result = (
                        supabase
                        .table("students")
                        .select("*")
                        .eq(
                            "admission_no",
                            admission_no.strip()
                        )
                        .eq(
                            "password",
                            password.strip()
                        )
                        .execute()
                    )

                    if result.data:

                        student = result.data[0]

                        st.session_state.logged_in = True

                        st.session_state.role = "student"

                        st.session_state.username = (
                            student["name"]
                        )

                        st.session_state.admission_no = (
                            student["admission_no"]
                        )

                        st.success(
                            "Student Login Successful!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Invalid Admission Number or Password."
                        )

                except Exception as e:

                    st.error(
                        f"Login Error: {e}"
                    )


    # =====================================================
    # STUDENT REGISTER
    # =====================================================

    with tab3:

        st.subheader(
            "📝 Student Registration"
        )

        st.info(
            "Admin द्वारा Student Record Add करने के बाद "
            "Admission Number से Registration करें."
        )

        admission_no = st.text_input(
            "Admission Number",
            key="register_admission"
        )

        password = st.text_input(
            "New Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm_password"
        )

        if st.button(
            "📝 Register",
            use_container_width=True
        ):

            if not admission_no:

                st.error(
                    "Admission Number required."
                )

            elif not password:

                st.error(
                    "Password required."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    result = (
                        supabase
                        .table("students")
                        .select("*")
                        .eq(
                            "admission_no",
                            admission_no.strip()
                        )
                        .execute()
                    )

                    if not result.data:

                        st.error(
                            "Admission Number नहीं मिला. "
                            "पहले Admin से Student Add करवाएं."
                        )

                    else:

                        (
                            supabase
                            .table("students")
                            .update({
                                "password": password
                            })
                            .eq(
                                "admission_no",
                                admission_no.strip()
                            )
                            .execute()
                        )

                        st.success(
                            "Registration Successful! "
                            "अब Student Login कर सकते हैं."
                        )

                except Exception as e:

                    st.error(
                        f"Registration Error: {e}"
                    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard():

    st.sidebar.title(
        "🏫 ADMIN PANEL"
    )

    st.sidebar.write(
        f"Welcome, {st.session_state.username}"
    )

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "👨‍🎓 Students",
            "👨‍🏫 Teachers",
            "👥 Faculty",
            "💰 Fees",
            "💳 Payment Approval",
            "🧾 Fee Receipts",
            "📅 Student Attendance",
            "📅 Teacher Attendance",
            "📝 Student Marks",
            "📊 Financial",
            "🏫 About School"
        ]
    )

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()


    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "🏠 Dashboard":

        st.title(
            "🏠 Admin Dashboard"
        )

        students = (
            supabase
            .table("students")
            .select("id")
            .execute()
        )

        teachers = (
            supabase
            .table("teachers")
            .select("id")
            .execute()
        )

        faculty = (
            supabase
            .table("faculty")
            .select("id")
            .execute()
        )

        payments = (
            supabase
            .table("payment_requests")
            .select("id")
            .eq(
                "status",
                "Pending"
            )
            .execute()
        )

        fees = (
            supabase
            .table("fees")
            .select(
                "total_fee,paid_amount,due_amount"
            )
            .execute()
        )

        total_fee = sum(
            float(x["total_fee"] or 0)
            for x in fees.data
        )

        paid = sum(
            float(x["paid_amount"] or 0)
            for x in fees.data
        )

        due = sum(
            float(x["due_amount"] or 0)
            for x in fees.data
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "👨‍🎓 Students",
            len(students.data)
        )

        c2.metric(
            "👨‍🏫 Teachers",
            len(teachers.data)
        )

        c3.metric(
            "👥 Faculty",
            len(faculty.data)
        )

        c4.metric(
            "⏳ Pending Payments",
            len(payments.data)
        )

        st.divider()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "💰 Total Fee",
            f"Rs. {total_fee:,.2f}"
        )

        c2.metric(
            "✅ Total Paid",
            f"Rs. {paid:,.2f}"
        )

        c3.metric(
            "📌 Total Due",
            f"Rs. {due:,.2f}"
        )


    # =====================================================
    # STUDENT MANAGEMENT
    # =====================================================

    elif menu == "👨‍🎓 Students":

        st.title(
            "👨‍🎓 Student Management"
        )

        tab1, tab2 = st.tabs(
            [
                "➕ Add Student",
                "📋 Student Records"
            ]
        )


        with tab1:

            with st.form(
                "add_student_form"
            ):

                c1, c2 = st.columns(2)

                with c1:

                    admission_no = st.text_input(
                        "Admission Number *"
                    )

                    name = st.text_input(
                        "Student Name *"
                    )

                    father_name = st.text_input(
                        "Father Name"
                    )

                    mother_name = st.text_input(
                        "Mother Name"
                    )

                    dob = st.date_input(
                        "Date of Birth"
                    )

                    gender = st.selectbox(
                        "Gender",
                        [
                            "Male",
                            "Female",
                            "Other"
                        ]
                    )

                with c2:

                    class_name = st.text_input(
                        "Class"
                    )

                    section = st.text_input(
                        "Section"
                    )

                    roll_no = st.text_input(
                        "Roll Number"
                    )

                    phone = st.text_input(
                        "Phone"
                    )

                    email = st.text_input(
                        "Email"
                    )

                    address = st.text_area(
                        "Address"
                    )

                submitted = st.form_submit_button(
                    "💾 Save Student",
                    use_container_width=True
                )

                if submitted:

                    if not admission_no or not name:

                        st.error(
                            "Admission Number और Name required हैं."
                        )

                    else:

                        try:

                            (
                                supabase
                                .table("students")
                                .insert({

                                    "admission_no":
                                        admission_no.strip(),

                                    "name":
                                        name.strip(),

                                    "father_name":
                                        father_name,

                                    "mother_name":
                                        mother_name,

                                    "dob":
                                        str(dob),

                                    "gender":
                                        gender,

                                    "class_name":
                                        class_name,

                                    "section":
                                        section,

                                    "roll_no":
                                        roll_no,

                                    "phone":
                                        phone,

                                    "email":
                                        email,

                                    "address":
                                        address

                                })
                                .execute()
                            )

                            st.success(
                                "Student Added Successfully!"
                            )

                        except Exception as e:

                            st.error(
                                f"Error: {e}"
                            )


        with tab2:

            result = (
                supabase
                .table("students")
                .select(
                    "admission_no,name,father_name,"
                    "class_name,section,roll_no,"
                    "phone,email,address"
                )
                .order(
                    "id",
                    desc=True
                )
                .execute()
            )

            if result.data:

                st.dataframe(
                    result.data,
                    use_container_width=True
                )

            else:

                st.info(
                    "No Student Records Found."
                )


    # =====================================================
    # TEACHERS
    # =====================================================

    elif menu == "👨‍🏫 Teachers":

        st.title(
            "👨‍🏫 Teacher Management"
        )

        with st.form(
            "teacher_form"
        ):

            c1, c2 = st.columns(2)

            with c1:

                teacher_id = st.text_input(
                    "Teacher ID *"
                )

                name = st.text_input(
                    "Teacher Name *"
                )

                subject = st.text_input(
                    "Subject"
                )

                qualification = st.text_input(
                    "Qualification"
                )

                joining_date = st.date_input(
                    "Joining Date"
                )

            with c2:

                phone = st.text_input(
                    "Phone"
                )

                email = st.text_input(
                    "Email"
                )

                address = st.text_area(
                    "Address"
                )

                salary = st.number_input(
                    "Monthly Salary",
                    min_value=0.0
                )

            submitted = st.form_submit_button(
                "💾 Save Teacher",
                use_container_width=True
            )

            if submitted:

                if not teacher_id or not name:

                    st.error(
                        "Teacher ID और Name required हैं."
                    )

                else:

                    try:

                        (
                            supabase
                            .table("teachers")
                            .insert({

                                "teacher_id":
                                    teacher_id,

                                "name":
                                    name,

                                "subject":
                                    subject,

                                "qualification":
                                    qualification,

                                "phone":
                                    phone,

                                "email":
                                    email,

                                "address":
                                    address,

                                "joining_date":
                                    str(joining_date),

                                "salary":
                                    salary

                            })
                            .execute()
                        )

                        st.success(
                            "Teacher Added Successfully!"
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )

        result = (
            supabase
            .table("teachers")
            .select("*")
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        st.dataframe(
            result.data,
            use_container_width=True
        )


    # =====================================================
    # FACULTY
    # =====================================================

    elif menu == "👥 Faculty":

        st.title(
            "👥 Faculty Management"
        )

        with st.form(
            "faculty_form"
        ):

            c1, c2 = st.columns(2)

            with c1:

                faculty_id = st.text_input(
                    "Faculty ID *"
                )

                name = st.text_input(
                    "Faculty Name *"
                )

                department = st.text_input(
                    "Department"
                )

                designation = st.text_input(
                    "Designation"
                )

                qualification = st.text_input(
                    "Qualification"
                )

            with c2:

                phone = st.text_input(
                    "Phone"
                )

                email = st.text_input(
                    "Email"
                )

                address = st.text_area(
                    "Address"
                )

                joining_date = st.date_input(
                    "Joining Date"
                )

                salary = st.number_input(
                    "Salary",
                    min_value=0.0
                )

            submitted = st.form_submit_button(
                "💾 Save Faculty",
                use_container_width=True
            )

            if submitted:

                try:

                    (
                        supabase
                        .table("faculty")
                        .insert({

                            "faculty_id":
                                faculty_id,

                            "name":
                                name,

                            "department":
                                department,

                            "designation":
                                designation,

                            "qualification":
                                qualification,

                            "phone":
                                phone,

                            "email":
                                email,

                            "address":
                                address,

                            "joining_date":
                                str(joining_date),

                            "salary":
                                salary

                        })
                        .execute()
                    )

                    st.success(
                        "Faculty Added Successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )

        result = (
            supabase
            .table("faculty")
            .select("*")
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        st.dataframe(
            result.data,
            use_container_width=True
        )


    # =====================================================
    # FEES
    # =====================================================

    elif menu == "💰 Fees":

        st.title(
            "💰 Fee Management"
        )

        students = (
            supabase
            .table("students")
            .select(
                "admission_no,name,class_name"
            )
            .execute()
        )

        if not students.data:

            st.warning(
                "पहले Student Add करें."
            )

        else:

            student_map = {

                f"{x['admission_no']} | "
                f"{x['name']} | "
                f"Class {x['class_name']}":
                x

                for x in students.data

            }

            selected = st.selectbox(
                "Select Student",
                list(
                    student_map.keys()
                )
            )

            student = student_map[selected]

            fee_type = st.selectbox(
                "Fee Type",
                [
                    "Admission Fee",
                    "Monthly Fee",
                    "Exam Fee",
                    "Transport Fee",
                    "Hostel Fee",
                    "Library Fee",
                    "Computer Fee",
                    "Other"
                ]
            )

            total_fee = st.number_input(
                "Total Fee",
                min_value=0.0
            )

            paid_amount = st.number_input(
                "Paid Amount",
                min_value=0.0
            )

            due_amount = max(
                total_fee - paid_amount,
                0
            )

            st.metric(
                "Due Amount",
                f"Rs. {due_amount:,.2f}"
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "eSewa",
                    "Khalti",
                    "Bank Transfer",
                    "Cheque"
                ]
            )

            remarks = st.text_area(
                "Remarks"
            )

            if st.button(
                "💾 Save Fee",
                use_container_width=True
            ):

                if paid_amount > total_fee:

                    st.error(
                        "Paid Amount Total Fee से ज्यादा नहीं हो सकता."
                    )

                else:

                    receipt_no = (
                        "REC-"
                        +
                        str(
                            uuid.uuid4()
                        )[:8].upper()
                    )

                    try:

                        (
                            supabase
                            .table("fees")
                            .insert({

                                "receipt_no":
                                    receipt_no,

                                "admission_no":
                                    student[
                                        "admission_no"
                                    ],

                                "student_name":
                                    student[
                                        "name"
                                    ],

                                "class_name":
                                    student[
                                        "class_name"
                                    ],

                                "fee_type":
                                    fee_type,

                                "total_fee":
                                    total_fee,

                                "paid_amount":
                                    paid_amount,

                                "due_amount":
                                    due_amount,

                                "payment_method":
                                    payment_method,

                                "payment_date":
                                    str(
                                        date.today()
                                    ),

                                "remarks":
                                    remarks

                            })
                            .execute()
                        )

                        if paid_amount > 0:

                            (
                                supabase
                                .table("finances")
                                .insert({

                                    "transaction_type":
                                        "Income",

                                    "category":
                                        fee_type,

                                    "amount":
                                        paid_amount,

                                    "description":
                                        f"Fee received from "
                                        f"{student['name']}",

                                    "transaction_date":
                                        str(
                                            date.today()
                                        )

                                })
                                .execute()
                            )

                        st.success(
                            f"Fee Saved Successfully! "
                            f"Receipt: {receipt_no}"
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


    # =====================================================
    # PAYMENT APPROVAL
    # =====================================================

    elif menu == "💳 Payment Approval":

        st.title(
            "💳 Student Payment Approval"
        )

        result = (
            supabase
            .table("payment_requests")
            .select("*")
            .eq(
                "status",
                "Pending"
            )
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        if not result.data:

            st.success(
                "No Pending Payment Requests."
            )

        for payment in result.data:

            with st.expander(
                f"💳 {payment['payment_id']} | "
                f"{payment['student_name']} | "
                f"Rs. {payment['amount']}"
            ):

                st.write(
                    f"Admission No: "
                    f"{payment['admission_no']}"
                )

                st.write(
                    f"Payment Method: "
                    f"{payment['payment_method']}"
                )

                st.write(
                    f"Transaction ID: "
                    f"{payment['transaction_id']}"
                )

                c1, c2 = st.columns(2)

                with c1:

                    if st.button(
                        "✅ Approve",
                        key=f"approve_{payment['id']}"
                    ):

                        fees = (
                            supabase
                            .table("fees")
                            .select("*")
                            .eq(
                                "admission_no",
                                payment[
                                    "admission_no"
                                ]
                            )
                            .gt(
                                "due_amount",
                                0
                            )
                            .order(
                                "id"
                            )
                            .limit(1)
                            .execute()
                        )

                        if fees.data:

                            fee = fees.data[0]

                            new_paid = (
                                float(
                                    fee[
                                        "paid_amount"
                                    ] or 0
                                )
                                +
                                float(
                                    payment[
                                        "amount"
                                    ]
                                )
                            )

                            new_due = max(
                                float(
                                    fee[
                                        "total_fee"
                                    ]
                                )
                                -
                                new_paid,
                                0
                            )

                            (
                                supabase
                                .table("fees")
                                .update({

                                    "paid_amount":
                                        new_paid,

                                    "due_amount":
                                        new_due

                                })
                                .eq(
                                    "id",
                                    fee["id"]
                                )
                                .execute()
                            )

                            (
                                supabase
                                .table(
                                    "payment_requests"
                                )
                                .update({

                                    "status":
                                        "Approved"

                                })
                                .eq(
                                    "id",
                                    payment["id"]
                                )
                                .execute()
                            )

                            (
                                supabase
                                .table("finances")
                                .insert({

                                    "transaction_type":
                                        "Income",

                                    "category":
                                        "Online Fee Payment",

                                    "amount":
                                        payment[
                                            "amount"
                                        ],

                                    "description":
                                        f"Online payment "
                                        f"from "
                                        f"{payment['student_name']}",

                                    "transaction_date":
                                        str(
                                            date.today()
                                        )

                                })
                                .execute()
                            )

                            st.success(
                                "Payment Approved!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Student का Due Fee Record नहीं मिला."
                            )

                with c2:

                    if st.button(
                        "❌ Reject",
                        key=f"reject_{payment['id']}"
                    ):

                        (
                            supabase
                            .table(
                                "payment_requests"
                            )
                            .update({

                                "status":
                                    "Rejected"

                            })
                            .eq(
                                "id",
                                payment["id"]
                            )
                            .execute()
                        )

                        st.warning(
                            "Payment Rejected."
                        )

                        st.rerun()


    # =====================================================
    # FEE RECEIPTS
    # =====================================================

    elif menu == "🧾 Fee Receipts":

        st.title(
            "🧾 Fee Receipts"
        )

        result = (
            supabase
            .table("fees")
            .select("*")
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        if result.data:

            st.dataframe(
                result.data,
                use_container_width=True
            )

        else:

            st.info(
                "No Fee Receipts Found."
            )


    # =====================================================
    # STUDENT ATTENDANCE
    # =====================================================

    elif menu == "📅 Student Attendance":

        st.title(
            "📅 Student Attendance"
        )

        students = (
            supabase
            .table("students")
            .select(
                "admission_no,name,class_name"
            )
            .execute()
        )

        if students.data:

            student_map = {

                f"{x['admission_no']} | "
                f"{x['name']}":
                x

                for x in students.data

            }

            selected = st.selectbox(
                "Select Student",
                list(
                    student_map.keys()
                )
            )

            student = student_map[selected]

            attendance_date = st.date_input(
                "Attendance Date"
            )

            status = st.selectbox(
                "Attendance Status",
                [
                    "Present",
                    "Absent",
                    "Late",
                    "Leave"
                ]
            )

            remarks = st.text_input(
                "Remarks"
            )

            if st.button(
                "💾 Save Student Attendance"
            ):

                try:

                    (
                        supabase
                        .table(
                            "student_attendance"
                        )
                        .insert({

                            "admission_no":
                                student[
                                    "admission_no"
                                ],

                            "student_name":
                                student[
                                    "name"
                                ],

                            "class_name":
                                student[
                                    "class_name"
                                ],

                            "attendance_date":
                                str(
                                    attendance_date
                                ),

                            "status":
                                status,

                            "remarks":
                                remarks

                        })
                        .execute()
                    )

                    st.success(
                        "Student Attendance Saved!"
                    )

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )


    # =====================================================
    # TEACHER ATTENDANCE
    # =====================================================

    elif menu == "📅 Teacher Attendance":

        st.title(
            "📅 Teacher Attendance"
        )

        teachers = (
            supabase
            .table("teachers")
            .select(
                "teacher_id,name"
            )
            .execute()
        )

        if teachers.data:

            teacher_map = {

                f"{x['teacher_id']} | "
                f"{x['name']}":
                x

                for x in teachers.data

            }

            selected = st.selectbox(
                "Select Teacher",
                list(
                    teacher_map.keys()
                )
            )

            teacher = teacher_map[selected]

            attendance_date = st.date_input(
                "Attendance Date"
            )

            status = st.selectbox(
                "Status",
                [
                    "Present",
                    "Absent",
                    "Late",
                    "Leave"
                ]
            )

            remarks = st.text_input(
                "Remarks"
            )

            if st.button(
                "💾 Save Teacher Attendance"
            ):

                try:

                    (
                        supabase
                        .table(
                            "teacher_attendance"
                        )
                        .insert({

                            "teacher_id":
                                teacher[
                                    "teacher_id"
                                ],

                            "teacher_name":
                                teacher[
                                    "name"
                                ],

                            "attendance_date":
                                str(
                                    attendance_date
                                ),

                            "status":
                                status,

                            "remarks":
                                remarks

                        })
                        .execute()
                    )

                    st.success(
                        "Teacher Attendance Saved!"
                    )

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )


    # =====================================================
    # STUDENT MARKS
    # =====================================================

    elif menu == "📝 Student Marks":

        st.title(
            "📝 Student Marks Management"
        )

        students = (
            supabase
            .table("students")
            .select(
                "admission_no,name,class_name"
            )
            .execute()
        )

        if students.data:

            student_map = {

                f"{x['admission_no']} | "
                f"{x['name']}":
                x

                for x in students.data

            }

            selected = st.selectbox(
                "Select Student",
                list(
                    student_map.keys()
                )
            )

            student = student_map[selected]

            exam_name = st.text_input(
                "Exam Name"
            )

            subject = st.text_input(
                "Subject"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                full_marks = st.number_input(
                    "Full Marks",
                    min_value=1.0,
                    value=100.0
                )

            with c2:

                pass_marks = st.number_input(
                    "Pass Marks",
                    min_value=0.0,
                    value=40.0
                )

            with c3:

                obtained_marks = st.number_input(
                    "Obtained Marks",
                    min_value=0.0,
                    max_value=full_marks
                )

            percentage = (
                obtained_marks
                /
                full_marks
                *
                100
            )

            grade = get_grade(
                percentage
            )

            st.info(
                f"Percentage: {percentage:.2f}% | "
                f"Grade: {grade}"
            )

            remarks = st.text_input(
                "Remarks"
            )

            if st.button(
                "💾 Save Marks"
            ):

                try:

                    (
                        supabase
                        .table("marks")
                        .insert({

                            "admission_no":
                                student[
                                    "admission_no"
                                ],

                            "student_name":
                                student[
                                    "name"
                                ],

                            "class_name":
                                student[
                                    "class_name"
                                ],

                            "exam_name":
                                exam_name,

                            "subject":
                                subject,

                            "full_marks":
                                full_marks,

                            "pass_marks":
                                pass_marks,

                            "obtained_marks":
                                obtained_marks,

                            "grade":
                                grade,

                            "remarks":
                                remarks

                        })
                        .execute()
                    )

                    st.success(
                        "Marks Saved Successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )


    # =====================================================
    # FINANCIAL
    # =====================================================

    elif menu == "📊 Financial":

        st.title(
            "📊 Financial Management"
        )

        transaction_type = st.selectbox(
            "Transaction Type",
            [
                "Income",
                "Expense"
            ]
        )

        category = st.text_input(
            "Category"
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0
        )

        description = st.text_area(
            "Description"
        )

        if st.button(
            "💾 Save Transaction"
        ):

            try:

                (
                    supabase
                    .table("finances")
                    .insert({

                        "transaction_type":
                            transaction_type,

                        "category":
                            category,

                        "amount":
                            amount,

                        "description":
                            description,

                        "transaction_date":
                            str(
                                date.today()
                            )

                    })
                    .execute()
                )

                st.success(
                    "Transaction Saved!"
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

        result = (
            supabase
            .table("finances")
            .select("*")
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        st.dataframe(
            result.data,
            use_container_width=True
        )


    # =====================================================
    # SCHOOL INFORMATION
    # =====================================================

    elif menu == "🏫 About School":

        st.title(
            "🏫 About School"
        )

        result = (
            supabase
            .table("school_info")
            .select("*")
            .limit(1)
            .execute()
        )

        old = (
            result.data[0]
            if result.data
            else {}
        )

        school_name = st.text_input(
            "School Name",
            value=old.get(
                "school_name",
                ""
            )
        )

        address = st.text_input(
            "Address",
            value=old.get(
                "address",
                ""
            )
        )

        phone = st.text_input(
            "Phone",
            value=old.get(
                "phone",
                ""
            )
        )

        email = st.text_input(
            "Email",
            value=old.get(
                "email",
                ""
            )
        )

        principal_name = st.text_input(
            "Principal Name",
            value=old.get(
                "principal_name",
                ""
            )
        )

        about = st.text_area(
            "About School",
            value=old.get(
                "about",
                ""
            )
        )

        if st.button(
            "💾 Save School Information"
        ):

            try:

                data = {

                    "school_name":
                        school_name,

                    "address":
                        address,

                    "phone":
                        phone,

                    "email":
                        email,

                    "principal_name":
                        principal_name,

                    "about":
                        about

                }

                if old:

                    (
                        supabase
                        .table("school_info")
                        .update(data)
                        .eq(
                            "id",
                            old["id"]
                        )
                        .execute()
                    )

                else:

                    (
                        supabase
                        .table("school_info")
                        .insert(data)
                        .execute()
                    )

                st.success(
                    "School Information Saved!"
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    admission_no = (
        st.session_state.admission_no
    )

    result = (
        supabase
        .table("students")
        .select("*")
        .eq(
            "admission_no",
            admission_no
        )
        .execute()
    )

    if not result.data:

        st.error(
            "Student Record Not Found."
        )

        return

    student = result.data[0]

    st.sidebar.title(
        "👨‍🎓 STUDENT PORTAL"
    )

    st.sidebar.write(
        f"Welcome, {student['name']}"
    )

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "👤 My Profile",
            "💰 My Fees",
            "💳 Pay Fee",
            "🧾 My Receipts",
            "📊 My Marks",
            "📅 My Attendance"
        ]
    )

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()


    # =====================================================
    # STUDENT DASHBOARD HOME
    # =====================================================

    if menu == "🏠 Dashboard":

        st.title(
            f"🏠 Welcome, {student['name']}"
        )

        fees = (
            supabase
            .table("fees")
            .select(
                "total_fee,paid_amount,due_amount"
            )
            .eq(
                "admission_no",
                admission_no
            )
            .execute()
        )

        total = sum(
            float(
                x["total_fee"] or 0
            )
            for x in fees.data
        )

        paid = sum(
            float(
                x["paid_amount"] or 0
            )
            for x in fees.data
        )

        due = sum(
            float(
                x["due_amount"] or 0
            )
            for x in fees.data
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "💰 Total Fee",
            f"Rs. {total:,.2f}"
        )

        c2.metric(
            "✅ Paid",
            f"Rs. {paid:,.2f}"
        )

        c3.metric(
            "📌 Due",
            f"Rs. {due:,.2f}"
        )


    # =====================================================
    # PROFILE
    # =====================================================

    elif menu == "👤 My Profile":

        st.title(
            "👤 My Profile"
        )

        for key, value in student.items():

            if key not in [
                "id",
                "password"
            ]:

                st.write(
                    f"**{key.replace('_', ' ').title()}:** "
                    f"{value}"
                )


    # =====================================================
    # MY FEES
    # =====================================================

    elif menu == "💰 My Fees":

        st.title(
            "💰 My Fee Details"
        )

        result = (
            supabase
            .table("fees")
            .select("*")
            .eq(
                "admission_no",
                admission_no
            )
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        if result.data:

            st.dataframe(
                result.data,
                use_container_width=True
            )

        else:

            st.info(
                "No Fee Records Found."
            )


    # =====================================================
    # PAY FEE
    # =====================================================

    elif menu == "💳 Pay Fee":

        st.title(
            "💳 Pay School Fee"
        )

        fees = (
            supabase
            .table("fees")
            .select(
                "due_amount"
            )
            .eq(
                "admission_no",
                admission_no
            )
            .execute()
        )

        due = sum(
            float(
                x["due_amount"] or 0
            )
            for x in fees.data
        )

        st.metric(
            "Current Due Amount",
            f"Rs. {due:,.2f}"
        )

        if due > 0:

            amount = st.number_input(
                "Payment Amount",
                min_value=1.0,
                max_value=due
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "eSewa",
                    "Khalti",
                    "Bank Transfer"
                ]
            )

            transaction_id = st.text_input(
                "Transaction ID"
            )

            remarks = st.text_area(
                "Remarks"
            )

            if st.button(
                "💳 Submit Payment Request",
                use_container_width=True
            ):

                if not transaction_id:

                    st.error(
                        "Transaction ID required."
                    )

                else:

                    payment_id = (
                        "PAY-"
                        +
                        str(
                            uuid.uuid4()
                        )[:8].upper()
                    )

                    try:

                        (
                            supabase
                            .table(
                                "payment_requests"
                            )
                            .insert({

                                "payment_id":
                                    payment_id,

                                "admission_no":
                                    admission_no,

                                "student_name":
                                    student[
                                        "name"
                                    ],

                                "amount":
                                    amount,

                                "payment_method":
                                    payment_method,

                                "transaction_id":
                                    transaction_id,

                                "payment_date":
                                    str(
                                        date.today()
                                    ),

                                "status":
                                    "Pending",

                                "remarks":
                                    remarks

                            })
                            .execute()
                        )

                        st.success(
                            "Payment Request Submitted Successfully!"
                        )

                        st.info(
                            f"Payment ID: {payment_id}"
                        )

                    except Exception as e:

                        st.error(
                            f"Payment Error: {e}"
                        )

        else:

            st.success(
                "🎉 आपका कोई Fee Due नहीं है!"
            )


    # =====================================================
    # RECEIPTS
    # =====================================================

    elif menu == "🧾 My Receipts":

        st.title(
            "🧾 My Fee Receipts"
        )

        result = (
            supabase
            .table("fees")
            .select("*")
            .eq(
                "admission_no",
                admission_no
            )
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        if not result.data:

            st.info(
                "No Receipts Found."
            )

        else:

            receipt_names = [

                x["receipt_no"]

                for x in result.data

            ]

            selected = st.selectbox(
                "Select Receipt",
                receipt_names
            )

            receipt = next(

                x

                for x in result.data

                if x["receipt_no"]
                ==
                selected

            )

            st.subheader(
                "🏫 FEE RECEIPT"
            )

            st.write(
                f"Receipt No: "
                f"{receipt['receipt_no']}"
            )

            st.write(
                f"Student: "
                f"{receipt['student_name']}"
            )

            st.write(
                f"Admission No: "
                f"{receipt['admission_no']}"
            )

            st.write(
                f"Class: "
                f"{receipt['class_name']}"
            )

            st.write(
                f"Total Fee: "
                f"Rs. {receipt['total_fee']}"
            )

            st.write(
                f"Paid: "
                f"Rs. {receipt['paid_amount']}"
            )

            st.write(
                f"Due: "
                f"Rs. {receipt['due_amount']}"
            )

            school_result = (
                supabase
                .table("school_info")
                .select("*")
                .limit(1)
                .execute()
            )

            school = (
                school_result.data[0]
                if school_result.data
                else {}
            )

            pdf_data = create_receipt_pdf(
                receipt,
                school
            )

            c1, c2 = st.columns(2)

            with c1:

                st.download_button(
                    "📄 Download Receipt",
                    data=pdf_data,
                    file_name=(
                        receipt[
                            "receipt_no"
                        ]
                        +
                        ".pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True
                )

            with c2:

                encoded_pdf = base64.b64encode(
                    pdf_data
                ).decode()

                print_html = f"""
                <html>
                <head>
                <title>Print Fee Receipt</title>
                </head>

                <body>

                <embed
                src="data:application/pdf;base64,{encoded_pdf}"
                width="100%"
                height="700px"
                type="application/pdf"
                />

                <script>

                window.onload = function() {{
                    setTimeout(
                        function() {{
                            window.print();
                        }},
                        1000
                    );
                }};

                </script>

                </body>
                </html>
                """

                encoded_html = base64.b64encode(
                    print_html.encode()
                ).decode()

                st.markdown(
                    f"""
                    <a
                    href="data:text/html;base64,{encoded_html}"
                    target="_blank"
                    style="
                    display:block;
                    background:#2563eb;
                    color:white;
                    padding:12px;
                    text-align:center;
                    border-radius:8px;
                    text-decoration:none;
                    font-weight:bold;
                    "
                    >
                    🖨️ Print Receipt
                    </a>
                    """,
                    unsafe_allow_html=True
                )


    # =====================================================
    # MY MARKS
    # =====================================================

    elif menu == "📊 My Marks":

        st.title(
            "📊 My Marks"
        )

        result = (
            supabase
            .table("marks")
            .select("*")
            .eq(
                "admission_no",
                admission_no
            )
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        if result.data:

            st.dataframe(
                result.data,
                use_container_width=True
            )

        else:

            st.info(
                "No Marks Records Found."
            )


    # =====================================================
    # MY ATTENDANCE
    # =====================================================

    elif menu == "📅 My Attendance":

        st.title(
            "📅 My Attendance"
        )

        result = (
            supabase
            .table(
                "student_attendance"
            )
            .select("*")
            .eq(
                "admission_no",
                admission_no
            )
            .order(
                "attendance_date",
                desc=True
            )
            .execute()
        )

        if result.data:

            st.dataframe(
                result.data,
                use_container_width=True
            )

        else:

            st.info(
                "No Attendance Records Found."
            )


# =========================================================
# MAIN APPLICATION
# =========================================================

if not st.session_state.logged_in:

    login_page()

else:

    if st.session_state.role == "admin":

        admin_dashboard()

    elif st.session_state.role == "student":

        student_dashboard()