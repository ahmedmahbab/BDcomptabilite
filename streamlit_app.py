from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# إعداد قاعدة البيانات
engine = create_engine('sqlite:///store.db')
Base = declarative_base()

# تعريف جدول المنتجات
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    tax_rate = Column(Float)
    quantity = Column(Integer)

# إنشاء الجداول في قاعدة البيانات
Base.metadata.create_all(engine)

# إعداد الجلسة للتفاعل مع قاعدة البيانات
Session = sessionmaker(bind=engine)
session = Session()
import streamlit as st

# إدخال بيانات السلعة
st.title("إدارة السلع")
product_name = st.text_input("اسم السلعة")
description = st.text_area("وصف السلعة")
price = st.number_input("السعر", min_value=0.0, step=0.01)
tax_rate = st.selectbox("نسبة الضريبة", [0, 9, 19])
quantity = st.number_input("الكمية المتاحة", min_value=0, step=1)

# إضافة السلعة إلى قاعدة البيانات
if st.button("إضافة السلعة"):
    new_product = Product(
        name=product_name,
        description=description,
        price=price,
        tax_rate=tax_rate,
        quantity=quantity
    )
    session.add(new_product)
    session.commit()
    st.success("تمت إضافة السلعة بنجاح!")
import pandas as pd

st.subheader("السلع المخزنة")
products = session.query(Product).all()

# تحويل البيانات إلى DataFrame لعرضها في الجدول
if products:
    df = pd.DataFrame([{
        "الاسم": p.name,
        "الوصف": p.description,
        "السعر": p.price,
        "الضريبة": p.tax_rate,
        "الكمية": p.quantity
    } for p in products])
    st.dataframe(df)
else:
    st.write("لا توجد سلع مدخلة بعد.")
# واجهة إصدار الفاتورة
st.title("إصدار فاتورة")

# اختيار السلعة والكمية
product_options = [p.name for p in products]
selected_product = st.selectbox("اختر السلعة", product_options)
selected_quantity = st.number_input("الكمية", min_value=1, step=1)

# طريقة الدفع
payment_method = st.selectbox("طريقة الدفع", ["نقداً", "صك", "إيداع بنكي"])

# البحث عن السلعة المختارة
product = next((p for p in products if p.name == selected_product), None)

# حساب الفاتورة والضرائب
if st.button("إصدار الفاتورة"):
    if product:
        total_price = product.price * selected_quantity
        tax_amount = total_price * (product.tax_rate / 100)
        total_with_tax = total_price + tax_amount
        
        # حساب ضريبة الطابع الجبائي إذا كان الدفع نقدًا
        stamp_tax = 0
        if payment_method == "نقداً":
            stamp_tax = total_with_tax * 0.01
        
        final_total = total_with_tax + stamp_tax
        
        st.write(f"المجموع قبل الضريبة: {total_price}")
        st.write(f"قيمة الضريبة: {tax_amount}")
        st.write(f"المجموع بعد الضريبة: {total_with_tax}")
        st.write(f"ضريبة الطابع الجبائي: {stamp_tax}")
        st.write(f"المجموع النهائي: {final_total}")
        
