import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# إنشاء الجداول إذا لم تكن موجودة
c.execute('''CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    company TEXT,
    amount REAL,
    type TEXT,
    sales REAL,
    purchases REAL
)''')
conn.commit()

st.set_page_config(page_title="لوحة تحكم شركة عجائب السيف", layout="wide")

st.title("📊 لوحة تحكم شركة عجائب السيف")

# قسم الإدخال
st.sidebar.header("إضافة بيانات جديدة")
date = st.sidebar.date_input("📅 التاريخ")
company = st.sidebar.text_input("🏢 الشركة")
amount = st.sidebar.number_input("💰 المصروفات", min_value=0.0, step=0.1)
sales = st.sidebar.number_input("📈 المبيعات", min_value=0.0, step=0.1)
purchases = st.sidebar.number_input("📦 المشتريات", min_value=0.0, step=0.1)
type_option = st.sidebar.selectbox("نوع العملية", ["مصروفات", "مبيعات", "مشتريات"])

if st.sidebar.button("➕ إضافة"):
    c.execute("INSERT INTO data (date, company, amount, type, sales, purchases) VALUES (?,?,?,?,?,?)",
              (str(date), company, amount, type_option, sales, purchases))
    conn.commit()
    st.sidebar.success("تمت إضافة العملية بنجاح ✅")

# جلب البيانات
df = pd.read_sql("SELECT * FROM data", conn)

if not df.empty:
    st.subheader("📋 البيانات المدخلة")
    st.dataframe(df)

    # حسابات إجمالية
    total_expenses = df["amount"].sum()
    total_sales = df["sales"].sum()
    total_purchases = df["purchases"].sum()
    net_profit = total_sales - (total_expenses + total_purchases)
    expense_ratio = (total_expenses / total_sales * 100) if total_sales > 0 else 0
    profit_ratio = (net_profit / total_sales * 100) if total_sales > 0 else 0

    st.metric("إجمالي المصروفات", f"{total_expenses:.2f} ريال")
    st.metric("إجمالي المبيعات", f"{total_sales:.2f} ريال")
    st.metric("إجمالي المشتريات", f"{total_purchases:.2f} ريال")
    st.metric("صافي الربح", f"{net_profit:.2f} ريال")
    st.metric("نسبة المصروفات من المبيعات", f"{expense_ratio:.2f}%")
    st.metric("نسبة الأرباح من المبيعات", f"{profit_ratio:.2f}%")

    # الرسوم البيانية
    st.subheader("📊 الرسوم البيانية")
    fig1 = px.bar(df, x="date", y="amount", color="company", title="المصروفات حسب الشركات")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(df, x="date", y="sales", title="المبيعات مع مرور الوقت")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("⚠️ لا توجد بيانات حتى الآن. الرجاء إدخال بيانات جديدة.")
