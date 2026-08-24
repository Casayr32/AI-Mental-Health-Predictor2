const mongoose = require('mongoose');

// Isticmaal MONGO_URI ama xiriirkaaga tooska ah haddii variable-ka la waayo
const mongoUri = process.env.MONGO_URI || process.env.MONGO_URL || 'mongodb+srv://ahmed:7451@cluster0.bhe2hmw.mongodb.net/mental_ai_care?retryWrites=true&w=majority&appName=Cluster0';

mongoose.connect(mongoUri, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => {
  console.log('✅ MongoDB Connected Successfully');
})
.catch((err) => {
  console.error('❌ MongoDB Connection Error: ', err.message);
});
