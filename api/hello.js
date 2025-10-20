// 가장 간단한 Vercel 함수 테스트
module.exports = (req, res) => {
    res.status(200).json({ 
        message: 'Hello from Vercel!',
        timestamp: new Date().toISOString()
    });
};

