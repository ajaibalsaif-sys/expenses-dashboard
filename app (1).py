import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# إنشاء قاعدة بيانات أو الاتصال بها
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# إنشاء الجداول إذا ما كانت موجودة
c.execute("""CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                company TEXT,
                expense REAL,
                sales REAL,
                purchases REAL
            )""")
conn.commit()

st.set_page_config(page_title="لوحة تحكم عجائب السيف", layout="wide")

st.title("📊 لوحة تحكم شركة عجائب السيف")

# 🟢 إدخال البيانات
st.subheader("➕ إدخال بيانات جديدة")

with st.form("data_entry", clear_on_submit=True):
    date = st.date_input("📅 التاريخ")
    company = st.text_input("🏢 الشركة")
    expense = st.number_input("💸 المصروفات", min_value=0.0, step=0.1)
    sales = st.number_input("💰 المبيعات", min_value=0.0, step=0.1)
    purchases = st.number_input("🛒 المشتريات", min_value=0.0, step=0.1)
    submitted = st.form_submit_button("💾 حفظ")

    if submitted:
        c.execute("INSERT INTO records (date, company, expense, sales, purchases) VALUES (?, ?, ?, ?, ?)",
                  (str(date), company, expense, sales, purchases))
        conn.commit()
        st.success("✅ تم إضافة البيانات بنجاح!")

# 🟡 قراءة البيانات من قاعدة البيانات
df = pd.read_sql("SELECT * FROM records", conn)

if not df.empty:
    st.subheader("📑 جميع البيانات")
    st.dataframe(df)

    # 🔹 الحسابات العامة
    total_sales = df["sales"].sum()
    total_expenses = df["expense"].sum()
    total_purchases = df["purchases"].sum()
    net_profit = total_sales - (total_expenses + total_purchases)

    # 🔹 النسب
    expense_ratio = (total_expenses / total_sales * 100) if total_sales > 0 else 0
    profit_ratio = (net_profit / total_sales * 100) if total_sales > 0 else 0

    # 🟢 عرض المؤشرات الرئيسية
    st.subheader("📌 المؤشرات الرئيسية")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("إجمالي المبيعات", f"{total_sales:,.2f}")
    col2.metric("إجمالي المصروفات", f"{total_expenses:,.2f}")
    col3.metric("إجمالي المشتريات", f"{total_purchases:,.2f}")
    col4.metric("صافي الربح", f"{net_profit:,.2f}")
    col5.metric("نسبة المصروفات من المبيعات", f"{expense_ratio:.2f}%")

    st.metric("نسبة الأرباح من المبيعات", f"{profit_ratio:.2f}%")

    # 🟣 الرسومات البيانية
    st.subheader("📈 التحليلات")
    fig1 = px.bar(df, x="date", y=["sales", "expense", "purchases"], barmode="group",
                  title="المبيعات والمصروفات والمشتريات حسب التاريخ")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.pie(names=["مصروفات", "مشتريات", "صافي الربح"],
                  values=[total_expenses, total_purchases, net_profit],
                  title="نسبة توزيع المصروفات والمشتريات وصافي الربح")
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("ℹ️ لم يتم إدخال أي بيانات حتى الآن.")
