const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const reportRoutes = require('./routes/reportRoutes');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();

// --- CORS CONFIGURATION (Saxitaanka CORS Error) ---
const allowedOrigins = [
    'https://zesty-speculoos-82d915.netlify.app',
    'http://localhost:5173',
    'http://localhost:3000'
];

app.use(cors({
    origin: function (origin, callback) {
        // Ogolaaw codsiyada aan lahayn origin (sida Postman/mobile apps) ama origin-ka ku jira allowedOrigins
        if (!origin || allowedOrigins.indexOf(origin) !== -1) {
            callback(null, true);
        } else {
            callback(null, true); // Ama u ogolaaw dhammaan marka lagu jiro horumarinta
        }
    },
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    credentials: true
}));

// Ka jawaabidda Preflight OPTIONS requests dhammaan marinnada
app.options('*', cors());

// Middlewares
app.use(express.json());

// Connect to MongoDB Atlas
const mongoUri = process.env.MONGO_URI || process.env.MONGO_URL || 'mongodb+srv://ahmed:7451@cluster0.bhe2hmw.mongodb.net/mental_ai_care?retryWrites=true&w=majority&appName=Cluster0';

mongoose.connect(mongoUri)
.then(() => {
    console.log('✅ MongoDB Connected Successfully');
})
.catch((err) => {
    console.error('❌ MongoDB Connection Error: ', err.message);
});

// --- API ROUTES ---
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/reports', reportRoutes);
app.use('/api/admin', require('./routes/adminRoutes'));
app.use('/api/patient', require('./routes/patientRoutes'));
app.use('/api/doctor', require('./routes/doctorRoutes'));

// Test & Root routes
app.get('/api/test', (req, res) => {
    res.json({ message: "MindCare AI Backend is running successfully!" });
});

app.get('/', (req, res) => {
    res.send("MindCare AI API Service is Active");
});

// Start Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
