document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('fetchInvoiceForm');
    const identifierInput = document.getElementById('identifier');
    const invoiceDetails = document.getElementById('invoiceDetails');
    const billNoSpan = document.getElementById('billNo');
    const customerNameSpan = document.getElementById('customerName');
    const dateTimeSpan = document.getElementById('dateTime');
    const downloadLink = document.getElementById('downloadLink');

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const identifier = identifierInput.value;

        fetch('/fetch_invoice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ identifier }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                billNoSpan.innerText = data.bill_no;
                customerNameSpan.innerText = data.customer_name;
                dateTimeSpan.innerText = data.date_time;
                downloadLink.href = data.pdf_url;
                invoiceDetails.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
