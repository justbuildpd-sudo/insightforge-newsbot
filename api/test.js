export default async (req, res) => {
    res.status(200).json({ 
        message: 'API is working!',
        url: req.url,
        method: req.method
    });
};

