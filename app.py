import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# إنشاء/الاتصال بقاعدة البيانات
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# إنشاء الجداول إذا ما كانت موجودة
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_number TEXT,
    amount REAL,
    company TEXT,
    category TEXT,
    date TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS sales_purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    sales REAL,
    purchases REAL
)
""")
conn.commit()

st.title("📊 لوحة تحكم مصروفات شركة عجائب السيف")

menu = ["إضافة مصروف", "إضافة مبيعات/مشتريات", "عرض التحليلات"]
choice = st.sidebar.selectbox("القائمة", menu)

# ---------------- إضافة مصروف ----------------
if choice == "إضافة مصروف":
    st.subheader("➕ إضافة مصروف جديد")
    expense_number = st.text_input("رقم الصرف")
    amount = st.number_input("المبلغ", min_value=0.0)
    company = st.text_input("اسم الشركة")
    category = st.text_input("البند / نوع الصرف")
    date = st.date_input("التاريخ")

    if st.button("حفظ المصروف"):
        c.execute("INSERT INTO expenses (expense_number, amount, company, category, date) VALUES (?, ?, ?, ?, ?)",
                  (expense_number, amount, company, category, str(date)))
        conn.commit()
        st.success("✅ تم إضافة المصروف بنجاح")

# ---------------- إضافة مبيعات ومشتريات ----------------
elif choice == "إضافة مبيعات/مشتريات":
    st.subheader("➕ إضافة بيانات المبيعات والمشتريات للشهر")
    month = st.text_input("الشهر (مثال: 2025-08)")
    sales = st.number_input("المبيعات", min_value=0.0)
    purchases = st.number_input("المشتريات", min_value=0.0)

    if st.button("حفظ البيانات"):
        c.execute("INSERT INTO sales_purchases (month, sales, purchases) VALUES (?, ?, ?)",
                  (month, sales, purchases))
        conn.commit()
        st.success("✅ تم إضافة بيانات المبيعات/المشتريات")

# ---------------- عرض التحليلات ----------------
elif choice == "عرض التحليلات":
    st.subheader("📈 التحليلات والتقارير")

    df_expenses = pd.read_sql("SELECT * FROM expenses", conn)
    df_sales = pd.read_sql("SELECT * FROM sales_purchases", conn)

    if not df_expenses.empty:
        st.write("### جميع المصروفات")
        st.dataframe(df_expenses)

        st.write("### إجمالي المصروفات")
        total = df_expenses["amount"].sum()
        st.metric("الإجمالي", f"{total:,.2f} ريال")

        st.write("### المصروفات لكل شركة")
        by_company = df_expenses.groupby("company")["amount"].sum()
        st.bar_chart(by_company)

        st.write("### المصروفات حسب التاريخ")
        df_expenses["date"] = pd.to_datetime(df_expenses["date"])
        by_date = df_expenses.groupby("date")["amount"].sum()
        st.line_chart(by_date)

    if not df_sales.empty:
        st.write("### المبيعات والمشتريات")
        st.dataframe(df_sales)

        fig, ax = plt.subplots()
        df_sales.set_index("month")[["sales", "purchases"]].plot(kind="bar", ax=ax)
        st.pyplot(fig)
