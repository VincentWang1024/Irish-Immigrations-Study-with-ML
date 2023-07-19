const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
<<<<<<< HEAD
      target: 'http://127.0.0.1:8000',
=======
      target: '${process.env.REACT_APP_NLP_PLATFORM_API_URL}',
>>>>>>> main
      changeOrigin: true,
    })
  );
};