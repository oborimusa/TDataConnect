cat > server.js << 'EOF'
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const PAYSTACK_SECRET_KEY = 'sk_test_db8bb39e4ef84a303b4bf63b7137a86a831fbc0e';

// GET endpoint for testing
app.get('/test', (req, res) => {
    res.send('Server is working! 🚀');
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        message: 'Server is running',
        timestamp: new Date().toISOString()
    });
});

// Initialize payment endpoint
app.post('/api/initialize-payment', async (req, res) => {
    console.log('📝 Payment request:', req.body);
    
    const { email, amount } = req.body;
    
    if (!email || !amount) {
        return res.status(400).json({ error: 'Email and amount required' });
    }
    
    try {
        const response = await fetch('https://api.paystack.co/transaction/initialize', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${PAYSTACK_SECRET_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                amount: amount * 100,
                callback_url: 'http://localhost:3000/callback'
            })
        });
        
        const data = await response.json();
        
        if (data.status) {
            res.json({ authorization_url: data.data.authorization_url });
        } else {
            res.status(400).json({ error: data.message });
        }
        
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Verify payment endpoint
app.post('/api/verify-payment', async (req, res) => {
    const { reference } = req.body;
    
    try {
        const response = await fetch(`https://api.paystack.co/transaction/verify/${reference}`, {
            headers: {
                'Authorization': `Bearer ${PAYSTACK_SECRET_KEY}`
            }
        });
        
        const data = await response.json();
        
        if (data.data && data.data.status === 'success') {
            res.json({ success: true, amount: data.data.amount / 100 });
        } else {
            res.json({ success: false });
        }
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`\n✅ Server running on http://localhost:${PORT}`);
    console.log(`📍 Test: http://localhost:${PORT}/test`);
    console.log(`📍 Health: http://localhost:${PORT}/api/health\n`);
});
EOF