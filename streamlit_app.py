import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from fpdf import FPDF
import pandas as pd
from num2words import num2words  # لتحويل الأرقام إلى كلمات

# إعداد قاعدة البيانات
engine = create_engine('sqlite:///store.db')  # قاعدة بيانات SQLite
Base = declarative_base()

# جدول الزبائن
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    commercial_register = Column(String)  # السجل التجاري
    tax_number = Column(String)  # الرقم الجبائي
    statistical_number = Column(String)  # الرقم الإحصائي
    material_number = Column(String)  # رقم المادة

# جدول الموردين (مع إضافة العنوان)
class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)  # العنوان
    commercial_register = Column(String)  # السجل التجاري
    tax_number = Column(String)  # الرقم الجبائي
    statistical_number = Column(String)  # الرقم الإحصائي
    material_number = Column(String)  # رقم المادة

# جدول معلومات التاجر (التي تظهر في الفاتورة)
class TraderInfo(Base):
    __tablename__ = 'trader_info'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    commercial_register = Column(String)  # السجل التجاري
    tax_number = Column(String)  # الرقم الجبائي
    statistical_number = Column(String)  # الرقم الإحصائي
    material_number = Column(String)  # رقم المادة

# جدول السلع
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    code = Column(String)  # رمز المنتج
    name = Column(String)
    purchase_price = Column(Float)  # ثمن الشراء
    selling_price = Column(Float)  # ثمن البيع
    tax_rate = Column(Float)  # نسبة الضريبة (0%, 9%, 19%)
    quantity = Column(Integer)  # الكمية المتاحة
    entry_date = Column(DateTime, default=datetime.now)  # تاريخ الإدخال
    purchase_invoice_number = Column(String)  # رقم فاتورة الشراء
    purchase_invoice_date = Column(DateTime)  # تاريخ فاتورة الشراء

# جدول الفواتير
class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship("Customer")
    date = Column(DateTime, default=datetime.now)
    payment_method = Column(String)
    total_amount = Column(Float)
    stamp_tax = Column(Float)

# جدول تفاصيل الفاتورة
class InvoiceItem(Base):
    __tablename__ = 'invoice_items'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    product = relationship("Product")
    price = Column(Float)  # السعر الذي تم فوترة السلعة به

# إنشاء الجداول (بما في ذلك إضافة الأعمدة الناقصة)
Base.metadata.create_all(engine)

# إعداد الجلسة للتفاعل مع قاعدة البيانات
Session = sessionmaker(bind=engine)
session = Session()

# التنقل بين الأقسام
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Sélectionnez une section",
    ["Info", "Fournisseurs", "Clients", "Entrée des produits", "Facturation", "Stock", "Afficher les factures"]
)

# إدارة معلومات التاجر
if section == "Info":
    st.title("Informations sur le commerçant")
    trader_info = session.query(TraderInfo).first()

    trader_name = st.text_input("Nom du commerçant", trader_info.name if trader_info else "")
    trader_commercial_register = st.text_input("Registre de commerce", trader_info.commercial_register if trader_info else "")
    trader_tax_number = st.text_input("Numéro fiscal", trader_info.tax_number if trader_info else "")
    trader_statistical_number = st.text_input("Numéro statistique", trader_info.statistical_number if trader_info else "")
    trader_material_number = st.text_input("Numéro de matériel", trader_info.material_number if trader_info else "")

    if st.button("Enregistrer / Mettre à jour les informations"):
        if trader_info:
            trader_info.name = trader_name
            trader_info.commercial_register = trader_commercial_register
            trader_info.tax_number = trader_tax_number
            trader_info.statistical_number = trader_statistical_number
            trader_info.material_number = trader_material_number
        else:
            new_trader_info = TraderInfo(
                name=trader_name,
                commercial_register=trader_commercial_register,
                tax_number=trader_tax_number,
                statistical_number=trader_statistical_number,
                material_number=trader_material_number
            )
            session.add(new_trader_info)
        session.commit()
        st.success("Informations mises à jour avec succès!")

# إدارة الموردين
elif section == "Fournisseurs":
    st.title("Gestion des fournisseurs")
    supplier_name = st.text_input("Nom du fournisseur")
    supplier_address = st.text_input("Adresse du fournisseur")
    supplier_commercial_register = st.text_input("Registre de commerce")
    supplier_tax_number = st.text_input("Numéro fiscal")
    supplier_statistical_number = st.text_input("Numéro statistique")
    supplier_material_number = st.text_input("Numéro de matériel")

    if st.button("Ajouter un fournisseur"):
        new_supplier = Supplier(
            name=supplier_name,
            address=supplier_address,
            commercial_register=supplier_commercial_register,
            tax_number=supplier_tax_number,
            statistical_number=supplier_statistical_number,
            material_number=supplier_material_number
        )
        session.add(new_supplier)
        session.commit()
        st.success("Fournisseur ajouté avec succès!")

    # عرض الموردين المدخلين في جدول مع إمكانية التعديل
    suppliers = session.query(Supplier).all()
    if suppliers:
        st.subheader("Liste des fournisseurs")
        for supplier in suppliers:
            st.write(f"Nom: {supplier.name}, Adresse: {supplier.address}, Registre de commerce: {supplier.commercial_register}, Numéro fiscal: {supplier.tax_number}")
            if st.button(f"Modifier {supplier.name}"):
                supplier_name = st.text_input("Nom du fournisseur", value=supplier.name)
                supplier_address = st.text_input("Adresse", value=supplier.address)
                supplier_commercial_register = st.text_input("Registre de commerce", value=supplier.commercial_register)
                supplier_tax_number = st.text_input("Numéro fiscal", value=supplier.tax_number)
                supplier_statistical_number = st.text_input("Numéro statistique", value=supplier.statistical_number)
                supplier_material_number = st.text_input("Numéro de matériel", value=supplier.material_number)

                if st.button(f"Enregistrer les modifications {supplier.name}"):
                    supplier.name = supplier_name
                    supplier.address = supplier_address
                    supplier.commercial_register = supplier_commercial_register
                    supplier.tax_number = supplier_tax_number
                    supplier.statistical_number = supplier_statistical_number
                    supplier.material_number = supplier_material_number
                    session.commit()
                    st.success(f"Fournisseur {supplier.name} mis à jour avec succès!")

# إدارة الزبائن
elif section == "Clients":
    st.title("Gestion des clients")
    customer_name = st.text_input("Nom du client")
    customer_address = st.text_input("Adresse du client")
    customer_phone = st.text_input("Numéro de téléphone")
    commercial_register = st.text_input("Registre de commerce")
    tax_number = st.text_input("Numéro fiscal")
    statistical_number = st.text_input("Numéro statistique")
    material_number = st.text_input("Numéro de matériel")

    if st.button("Ajouter un client"):
        new_customer = Customer(
            name=customer_name, 
            address=customer_address, 
            phone=customer_phone,
            commercial_register=commercial_register, 
            tax_number=tax_number,
            statistical_number=statistical_number, 
            material_number=material_number
        )
        session.add(new_customer)
        session.commit()
        st.success("Client ajouté avec succès!")
    
    # عرض الزبائن المدخلين في جدول مع إمكانية التعديل
    customers = session.query(Customer).all()
    if customers:
        df_customers = pd.DataFrame([(cust.id, cust.name, cust.address, cust.phone) for cust in customers], 
                                    columns=['ID', 'Nom', 'Adresse', 'Téléphone'])
        st.dataframe(df_customers)

        selected_customer_id = st.selectbox("Sélectionner un client à modifier", df_customers['ID'])
        selected_customer = session.query(Customer).get(selected_customer_id)

        if selected_customer:
            customer_name = st.text_input("Nom du client", selected_customer.name)
            customer_address = st.text_input("Adresse du client", selected_customer.address)
            customer_phone = st.text_input("Numéro de téléphone", selected_customer.phone)
            commercial_register = st.text_input("Registre de commerce", selected_customer.commercial_register)
            tax_number = st.text_input("Numéro fiscal", selected_customer.tax_number)
            statistical_number = st.text_input("Numéro statistique", selected_customer.statistical_number)
            material_number = st.text_input("Numéro de matériel", selected_customer.material_number)

            if st.button(f"Enregistrer les modifications pour {selected_customer.name}"):
                selected_customer.name = customer_name
                selected_customer.address = customer_address
                selected_customer.phone = customer_phone
                selected_customer.commercial_register = commercial_register
                selected_customer.tax_number = tax_number
                selected_customer.statistical_number = statistical_number
                selected_customer.material_number = material_number
                session.commit()
                st.success(f"Client {selected_customer.name} mis à jour avec succès!")

# قسم خاص بإدخال السلع
elif section == "Entrée des produits":
    st.title("Entrée des produits")

    product_code = st.text_input("Code du produit")
    product_name = st.text_input("Nom du produit")
    purchase_price = st.number_input("Prix d'achat", min_value=0.0, step=0.01)
    selling_price = st.number_input("Prix de vente", min_value=0.0, step=0.01)
    tax_rate = st.selectbox("Taux de TVA", [0, 9, 19])
    product_quantity = st.number_input("Quantité achetée", min_value=0, step=1)
    purchase_invoice_number = st.text_input("Numéro de la facture d'achat")
    purchase_invoice_date = st.date_input("Date de la facture d'achat", value=datetime.now())

    if st.button("Ajouter un produit"):
        # تحقق إذا كان المنتج موجود بالفعل
        existing_product = session.query(Product).filter_by(code=product_code).first()
        
        if existing_product:
            # إذا كان المنتج موجودًا، دمج الكمية الجديدة مع الكمية القديمة
            existing_product.quantity += product_quantity
        else:
            # إذا كان المنتج غير موجود، أضف منتجًا جديدًا
            new_product = Product(
                code=product_code, 
                name=product_name,
                purchase_price=purchase_price, 
                selling_price=selling_price,
                tax_rate=tax_rate, 
                quantity=product_quantity,
                purchase_invoice_number=purchase_invoice_number, 
                purchase_invoice_date=purchase_invoice_date
            )
            session.add(new_product)

        session.commit()
        st.success("Produit ajouté ou mis à jour avec succès!")

# قسم الفوترة
elif section == "Facturation":
    st.title("Émission de la facture")

    # اختيار الزبون
    customers = session.query(Customer).all()
    customer_options = [f"{c.id}: {c.name}" for c in customers]
    selected_customer = st.selectbox("Choisir un client", customer_options)

    # اختيار السلع
    products = session.query(Product).all()
    product_options = [f"{p.code}: {p.name}" for p in products]  # عرض كود المنتج و اسمه
    selected_products = st.multiselect("Choisir des produits", product_options)

    # استرجاع كائنات المنتجات بناءً على الكود المختار
    selected_product_objects = [
        session.query(Product).filter_by(code=product_option.split(":")[0].strip()).first() 
        for product_option in selected_products
    ]

    # إدخال الكميات لكل سلعة
    product_quantities = {
        product.code: st.number_input(f"Quantité de {product.name} (Code: {product.code})", min_value=1, max_value=product.quantity)
        for product in selected_product_objects
    }

    # اختيار طريقة الدفع
    payment_method = st.selectbox("Méthode de paiement", ["Espèces", "Chèque", "Virement bancaire"])

    if st.button("Émettre la facture"):
        # البحث عن الزبون المختار
        customer_id = int(selected_customer.split(":")[0])
        customer = session.query(Customer).get(customer_id)

        # البحث عن معلومات التاجر لإضافتها إلى الفاتورة
        trader_info = session.query(TraderInfo).first()

        # حساب المجموع الإجمالي وضريبة القيمة المضافة
        total_amount = 0
        total_tax = 0
        invoice = Invoice(customer=customer, payment_method=payment_method)
        session.add(invoice)
        session.commit()

        invoice_data = []
        is_quantity_available = True

        for product in selected_product_objects:
            quantity = product_quantities[product.code]
            if quantity > product.quantity:
                st.warning(f"La quantité demandée de {product.name} (Code: {product.code}) n'est pas disponible.")
                is_quantity_available = False
                break
            else:
                # خصم الكمية من المخزن
                product.quantity -= quantity

                # المجموع الأولي (prix_total_produit)
                prix_total_produit = product.selling_price * quantity

                # حساب الضريبة (TVA)
                tax_amount = prix_total_produit * (product.tax_rate / 100)

                # المجموع النهائي بعد الضريبة
                total_product = prix_total_produit + tax_amount

                total_tax += tax_amount
                total_amount += total_product

                # إضافة السلعة إلى الفاتورة
                invoice_item = InvoiceItem(invoice_id=invoice.id, product_id=product.id, quantity=quantity, price=product.selling_price)
                session.add(invoice_item)

                # تخزين البيانات في قائمة لعرضها في الجدول
                invoice_data.append({
                    'Code du produit': product.code,
                    'Nom du produit': product.name,
                    'Quantité': quantity,
                    'Prix unitaire': product.selling_price,
                    'Prix total': prix_total_produit,
                    'TVA': tax_amount,
                    'Total': total_product
                })

        # إذا كانت الكميات متوفرة
        if is_quantity_available:
            # حساب ضريبة الطابع الجبائي إذا كانت طريقة الدفع نقدًا
            stamp_tax = 0
            if payment_method == "Espèces":
                stamp_tax = total_amount * 0.01

            # تحديث المجموع الإجمالي
            invoice.total_amount = total_amount + stamp_tax
            invoice.stamp_tax = stamp_tax
            session.commit()

            # عرض الفاتورة كجدول
            st.subheader(f"Facture pour le client: {customer.name}")
            df_invoice = pd.DataFrame(invoice_data)
            st.dataframe(df_invoice)

            # إنشاء ملف PDF للفاتورة باستخدام FPDF
            pdf = FPDF()
            pdf.add_page()

            # تحميل الخط DejaVuSansCondensed
            pdf.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)  # تأكد من أن الخط موجود في المجلد الصحيح

            # تكبير كلمة FACTURE
            pdf.set_font('DejaVu', '', 24)
            pdf.cell(200, 10, txt="FACTURE", ln=True, align='C')

            # تصغير معلومات الزبون
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(100, 10, txt=f"Numéro de facture: {invoice.id}")
            pdf.cell(100, 10, txt=f"Date: {invoice.date.strftime('%Y-%m-%d')}", ln=True)
            pdf.cell(100, 10, txt=f"Nom du client: {customer.name}")
            pdf.cell(100, 10, txt=f"Adresse: {customer.address}", ln=True)
            pdf.cell(100, 10, txt=f"Registre de commerce: {customer.commercial_register}")
            pdf.cell(100, 10, txt=f"Numéro fiscal: {customer.tax_number}", ln=True)
            pdf.cell(100, 10, txt=f"Numéro statistique: {customer.statistical_number}")
            pdf.cell(100, 10, txt=f"Numéro de matériel: {customer.material_number}", ln=True)

            # إضافة معلومات التاجر إلى الفاتورة
            if trader_info:
                pdf.cell(100, 10, txt=f"Nom du commerçant: {trader_info.name}")
                pdf.cell(100, 10, txt=f"Registre de commerce: {trader_info.commercial_register}", ln=True)
                pdf.cell(100, 10, txt=f"Numéro fiscal: {trader_info.tax_number}")
                pdf.cell(100, 10, txt=f"Numéro statistique: {trader_info.statistical_number}")
                pdf.cell(100, 10, txt=f"Numéro de matériel: {trader_info.material_number}", ln=True)

            # تفاصيل السلع في الفاتورة - باستخدام جدول
            pdf.ln(10)
            pdf.set_font('DejaVu', '', 12)
            pdf.cell(40, 10, txt="Code", border=1)
            pdf.cell(40, 10, txt="Produit", border=1)
            pdf.cell(40, 10, txt="Quantité", border=1)
            pdf.cell(40, 10, txt="Prix unitaire", border=1)
            pdf.cell(40, 10, txt="Prix total", border=1)
            pdf.cell(40, 10, txt="TVA", border=1)
            pdf.cell(40, 10, txt="Total", border=1, ln=True)

            for item in invoice_data:
                pdf.cell(40, 10, txt=item['Code du produit'], border=1)
                pdf.cell(40, 10, txt=item['Nom du produit'], border=1)
                pdf.cell(40, 10, txt=str(item['Quantité']), border=1)
                pdf.cell(40, 10, txt=str(item['Prix unitaire']), border=1)
                pdf.cell(40, 10, txt=str(item['Prix total']), border=1)
                pdf.cell(40, 10, txt=str(item['TVA']), border=1)
                pdf.cell(40, 10, txt=str(item['Total']), border=1, ln=True)

            # المجموع الكلي بالأرقام
            pdf.set_font('DejaVu', '', 14)
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Montant total: {invoice.total_amount} DZD", ln=True)

            # المجموع الكلي بالحروف
            total_in_words = num2words(invoice.total_amount, lang='fr')
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Montant total (en lettres): {total_in_words.capitalize()} dinars", ln=True)

            # حفظ ملف PDF
            pdf_output = f"Facture_{invoice.id}.pdf"
            pdf.output(pdf_output)

            # عرض زر تنزيل الفاتورة
            with open(pdf_output, "rb") as pdf_file:
                st.download_button(label="Télécharger la facture PDF", data=pdf_file, file_name=pdf_output, mime="application/octet-stream")

# إدارة المخزن
elif section == "Stock":
    st.title("Gestion du stock")
    
    # عرض السلع المتاحة فقط
    products = session.query(Product).all()

    if products:
        # دمج الكميات المتكررة بناءً على الكود والاسم
        product_stock = {}
        for prod in products:
            if prod.code in product_stock:
                product_stock[prod.code]['Quantité disponible'] += prod.quantity
            else:
                product_stock[prod.code] = {
                    'Code': prod.code,
                    'Nom': prod.name,
                    'Quantité disponible': prod.quantity
                }

        df_stock = pd.DataFrame(product_stock.values(), columns=['Code', 'Nom', 'Quantité disponible'])
        st.dataframe(df_stock)

# عرض الفواتير السابقة مع إمكانية إعادة الطباعة
elif section == "Afficher les factures":
    st.title("Afficher les factures précédentes")

    # استرجاع جميع الفواتير من قاعدة البيانات
    invoices = session.query(Invoice).all()

    # التحقق إذا كانت هناك فواتير في قاعدة البيانات
    if len(invoices) > 0:
        # إنشاء قائمة بالفواتير المتاحة لعرضها
        invoice_options = [f"Facture N° {inv.id} - {inv.date.strftime('%Y-%m-%d')}" for inv in invoices]
        
        # اختيار فاتورة لعرضها
        selected_invoice = st.selectbox("Choisissez une facture", invoice_options)

        # الحصول على الفاتورة المختارة
        invoice_id = int(selected_invoice.split()[2])
        invoice = session.query(Invoice).get(invoice_id)

        # عرض تفاصيل الفاتورة
        st.subheader(f"Facture N° {invoice.id}")
        st.write(f"Date d'émission: {invoice.date.strftime('%Y-%m-%d')}")
        st.write(f"Nom du client: {invoice.customer.name}")
        st.write(f"Montant total: {invoice.total_amount} DZD")
        st.write(f"Méthode de paiement: {invoice.payment_method}")

        # استرجاع تفاصيل المنتجات المشتراة في الفاتورة
        invoice_items = session.query(InvoiceItem).filter_by(invoice_id=invoice.id).all()
        if invoice_items:
            invoice_data = []
            for item in invoice_items:
                product = session.query(Product).get(item.product_id)
                invoice_data.append({
                    'Code du produit': product.code,
                    'Nom du produit': product.name,
                    'Quantité': item.quantity,
                    'Prix unitaire': item.price,  # استخدام السعر من الفاتورة وليس المنتج
                    'TVA': item.price * (product.tax_rate / 100),
                    'Total': (item.price + item.price * (product.tax_rate / 100)) * item.quantity
                })

            df_invoice = pd.DataFrame(invoice_data)
            st.dataframe(df_invoice)

            # زر لإعادة طباعة الفاتورة كملف PDF
            if st.button("Réimprimer la facture"):
                # إنشاء ملف PDF للفاتورة باستخدام FPDF
                pdf = FPDF()
                pdf.add_page()

                # تحميل الخط DejaVuSansCondensed
                pdf.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)  # تأكد من أن الخط موجود في المجلد الصحيح

                # تكبير كلمة FACTURE
                pdf.set_font('DejaVu', '', 24)
                pdf.cell(200, 10, txt="FACTURE", ln=True, align='C')

                # تصغير معلومات الزبون
                pdf.set_font('DejaVu', '', 10)
                pdf.cell(100, 10, txt=f"Numéro de facture: {invoice.id}")
                pdf.cell(100, 10, txt=f"Date: {invoice.date.strftime('%Y-%m-%d')}", ln=True)
                pdf.cell(100, 10, txt=f"Nom du client: {invoice.customer.name}")
                pdf.cell(100, 10, txt=f"Adresse: {invoice.customer.address}", ln=True)
                pdf.cell(100, 10, txt=f"Registre de commerce: {invoice.customer.commercial_register}")
                pdf.cell(100, 10, txt=f"Numéro fiscal: {invoice.customer.tax_number}", ln=True)
                pdf.cell(100, 10, txt=f"Numéro statistique: {invoice.customer.statistical_number}")
                pdf.cell(100, 10, txt=f"Numéro de matériel: {invoice.customer.material_number}", ln=True)

                # تفاصيل السلع في الفاتورة - باستخدام جدول
                pdf.ln(10)
                pdf.set_font('DejaVu', '', 12)
                pdf.cell(40, 10, txt="Code", border=1)
                pdf.cell(40, 10, txt="Produit", border=1)
                pdf.cell(40, 10, txt="Quantité", border=1)
                pdf.cell(40, 10, txt="Prix unitaire", border=1)
                pdf.cell(40, 10, txt="TVA", border=1)
                pdf.cell(40, 10, txt="Total", border=1, ln=True)

                for item in invoice_data:
                    pdf.cell(40, 10, txt=item['Code du produit'], border=1)
                    pdf.cell(40, 10, txt=item['Nom du produit'], border=1)
                    pdf.cell(40, 10, txt=str(item['Quantité']), border=1)
                    pdf.cell(40, 10, txt=str(item['Prix unitaire']), border=1)
                    pdf.cell(40, 10, txt=str(item['TVA']), border=1)
                    pdf.cell(40, 10, txt=str(item['Total']), border=1, ln=True)

                # المجموع الكلي بالأرقام
                pdf.set_font('DejaVu', '', 14)
                pdf.ln(10)
                pdf.cell(200, 10, txt=f"Montant total: {invoice.total_amount} DZD", ln=True)

                # المجموع الكلي بالحروف
                total_in_words = num2words(invoice.total_amount, lang='fr')
                pdf.ln(10)
                pdf.cell(200, 10, txt=f"Montant total (en lettres): {total_in_words.capitalize()} dinars", ln=True)

                # حفظ ملف PDF
                pdf_output = f"Facture_{invoice.id}.pdf"
                pdf.output(pdf_output)

                # عرض زر تنزيل الفاتورة
                with open(pdf_output, "rb") as pdf_file:
                    st.download_button(label="Télécharger la facture PDF", data=pdf_file, file_name=pdf_output, mime="application/octet-stream")
        else:
            st.write("Aucun article trouvé pour cette facture.")
    else:
        st.write("Aucune facture disponible.")
