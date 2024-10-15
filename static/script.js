document.addEventListener("DOMContentLoaded", () => {
    const addItemButton = document.getElementById('addItemButton');
    const billingItemsTable = document.getElementById('billingItemsTable');
    const totalAmountElement = document.getElementById('totalAmount');
    const generateInvoiceButton = document.getElementById('generateInvoiceButton');

    function calculateTotal() {
        let total = 0;
        document.querySelectorAll('.item-total').forEach(itemTotalElement => {
            total += parseFloat(itemTotalElement.innerText) || 0;
        });
        totalAmountElement.innerText = total.toFixed(2);
    }

    function updateTotal() {
        const rows = billingItemsTable.querySelectorAll('tr');
        rows.forEach(row => {
            const quantity = row.querySelector('.item-quantity').value;
            const price = row.querySelector('.item-price').value;
            const totalCell = row.querySelector('.item-total');
            if (quantity && price) {
                totalCell.innerText = (quantity * price).toFixed(2);
            } else {
                totalCell.innerText = '0.00';
            }
        });
        calculateTotal();
    }

    function cancelItem(event) {
        const row = event.target.closest('tr');
        if (row) {
            row.remove();
            calculateTotal();
        }
    }

    addItemButton.addEventListener('click', () => {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" class="item-description" placeholder="Item Description"></td>
            <td><input type="number" class="item-quantity" value="1"></td>
            <td><input type="number" class="item-price" value="0.00"></td>
            <td class="item-total">0.00</td>
            <td><button class="cancelItemButton">Cancel</button></td>
        `;
        billingItemsTable.appendChild(newRow);

        // Attach event listener for the new cancel button
        newRow.querySelector('.cancelItemButton').addEventListener('click', cancelItem);

        // Update total after adding a new item
        updateTotal();
    });

    billingItemsTable.addEventListener('input', updateTotal);

    // Attach event listeners to existing cancel buttons
    document.querySelectorAll('.cancelItemButton').forEach(button => {
        button.addEventListener('click', cancelItem);
    });

    generateInvoiceButton.addEventListener('click', () => {
        const customerName = document.getElementById('customerName').value;
        const customerEmail = document.getElementById('customerEmail').value;
        const billingItems = [];

        const rows = billingItemsTable.querySelectorAll('tr');
        rows.forEach(row => {
            const description = row.querySelector('.item-description').value;
            const quantity = row.querySelector('.item-quantity').value;
            const price = row.querySelector('.item-price').value;
            const total = row.querySelector('.item-total').innerText;
            if(description && quantity && price && total) {
                billingItems.push({ description, quantity, price, total });
            }
        });

        const totalAmount = totalAmountElement.innerText;

        fetch('/generate_invoice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                customerName,
                customerEmail,
                billingItems,
                totalAmount
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
