from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate,Table, TableStyle, Paragraph, Spacer
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# MySQL connection details
db_config = {
    'user': 'DB username',
    'password': 'your db password',
    'host': 'localhost',
    'database': 'your db name'
}

def generate_pdf(bill_no, customer_name, phone_no, billing_items, totalAmount):
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    elements = []
    header = [
        Paragraph(f"Invoice Number: {bill_no}", normal_style),
        Paragraph(f"Customer Name: {customer_name}", normal_style),
        Paragraph(f"Phone Number: {phone_no}", normal_style),
        Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style),
        Spacer(1, 12)
    ]
    
    elements.extend(header)
    
    # Create table data
    table_data = [["Item", "Quantity", "Price", "Total"]]
    
    for item in billing_items:
        # Convert to float if needed
        description = item.get('description', '')
        quantity = str(item.get('quantity', '0'))
        price = float(item.get('price', 0.0))
        total = float(item.get('total', 0.0))
        
        table_data.append([
            description,
            quantity,
            f"{price:.2f}",
            f"{total:.2f}"
        ])
    
    # Add total amount row
    table_data.append(["", "", "Total Amount:", f"{float(totalAmount):.2f}"])
    
    # Create table
    table = Table(table_data, colWidths=[200, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT')
    ]))
    
    elements.append(table)
    
    pdf.build(elements)
    
    pdf_buffer.seek(0)
    return pdf_buffer.read()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cashier')
def cashier():
    return render_template('cashier.html')

@app.route('/login_cashier', methods=['POST'])
def login_cashier():
    cashier_id = request.form.get('cashier_id')
    password = request.form.get('password')

    # Simple cashier authentication (you can expand this)
    if cashier_id == 'admin' and password == 'password':
        return redirect(url_for('bill'))
    else:
        return "Invalid credentials", 401

@app.route('/bill')
def bill():
    return render_template('bill.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')

@app.route('/fetch_invoice', methods=['POST'])
def fetch_invoice():
    identifier = request.form.get('identifier')

    if not identifier:
        return render_template('customer.html', error='Identifier is required')

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Query by phone number or bill number
        query = """
        SELECT Bill_No, Customers_name, Bill_date, Invoice_pdf
        FROM customers
        WHERE Phone_no = %s OR Bill_No = %s
        """
        cursor.execute(query, (identifier, identifier))
        
        result = cursor.fetchone()

        if not result:
            return render_template('customer.html', error='No invoice found for the provided identifier')

        bill_no, customer_name, bill_date, pdf_data = result

        # Save PDF to a temporary file or a URL if using a server
        pdf_url = f'static/{bill_no}.pdf'
        with open(f'static/{bill_no}.pdf', 'wb') as f:
            f.write(pdf_data)

        invoice = {
            'bill_no': bill_no,
            'customer_name': customer_name,
            'date_time': bill_date.strftime('%Y-%m-%d %H:%M:%S'),
            'pdf_url': pdf_url
        }

        return render_template('customer.html', invoice=invoice)

    # except mysql.connector.Error as err:
    #     return render_template('customer.html', error=f"Database error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# API to handle invoice submission and store in DB
@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    
    customer_name = data.get('customerName')
    phone_no = data.get('customerEmail')
    billing_items = data.get('billingItems')
    totalAmount = data.get('totalAmount')
    
    if not customer_name or not phone_no:
        return jsonify({'error': 'Customer Name and Phone Number are required'}), 400
    
    if not billing_items or not isinstance(billing_items, list):
        return jsonify({'error': 'Billing Items must be a list'}), 400
    
    # Generate a new bill number
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    result = cursor.fetchone()
    bill_no = result[0] + 1
    cursor.close()
    connection.close()

    # Generate PDF
    pdf_data = generate_pdf(bill_no, customer_name, phone_no, billing_items, totalAmount)

    # Connect to MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Insert invoice data into the database
    insert_query = """
    INSERT INTO [your table name] (Bill_No, Bill_date, Customers_name, Phone_no, Invoice_pdf)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (bill_no, datetime.now(), customer_name, phone_no, pdf_data))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'message': 'Invoice generated successfully', 'bill_no': bill_no})

if __name__ == '__main__':
    app.run(debug=True)
