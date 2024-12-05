//--------------------------------------------only theMet--------------------------------------------
// const express = require('express');
// const axios = require('axios');
// const app = express();

// app.use(express.json());

// // Enable CORS for all requests
// app.use((req, res, next) => {
//     res.header('Access-Control-Allow-Origin', '*');
//     res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
//     res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
//     next();
// });

// // Proxy endpoint to handle find_similar requests
// app.post('/api/find_similar', async (req, res) => {
//     try {
//         console.log('Received request to /api/find_similar');
//         console.log('Request body:', req.body);

//         // Forward the request to your Flask server, including top_k: 16
//         const response = await axios.post('http://127.0.0.1:5000/find_similar', {
//             objectID: req.body.objectID,
//             top_k: 16  // Pass 16 similar images
//         });

//         res.json(response.data);
//     } catch (error) {
//         console.error('Error fetching similar images:', error.response ? error.response.status : error.message);
//         res.status(500).send('Error fetching similar images.');
//     }
// });

// // Start the server
// app.listen(3001, () => {
//     console.log('Proxy server running on port 3001');
// }); 
//--------------------------------------------only theMet--------------------------------------------

const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

// Enable CORS for all requests
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    next();
});

// Proxy endpoint to handle find_similar requests
app.post('/api/find_similar', async (req, res) => {
    try {
        console.log('Received request to /api/find_similar');
        console.log('Request body:', req.body);

        // Forward the request to your Flask server, including collection and top_k
        const response = await axios.post('http://127.0.0.1:5000/find_similar', {
            objectID: req.body.objectID,
            collection: req.body.collection,
            top_k: 16  // Pass 16 similar images
        });

        res.json(response.data);
    } catch (error) {
        console.error('Error fetching similar images:', error.response ? error.response.data : error.message);
        res.status(500).send('Error fetching similar images.');
    }
});

// Start the server
app.listen(3001, () => {
    console.log('Proxy server running on port 3001');
});
