document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Simulate login validation
    const cashierId = document.getElementById('cashierId').value;
    const password = document.getElementById('password').value;

    // Validate credentials (for demonstration purposes, hardcoded)
    if (cashierId === '1234' && password === 'password') {
        window.location.href = '/bill'; // Redirect to invoice generation page
    } else {
        alert('Invalid credentials');
    }
});