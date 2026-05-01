import { randomUUID } from 'crypto';

export function correlationId(req, res, next) {
  req.correlationId = req.headers['x-correlation-id'] || randomUUID();
  res.setHeader('x-correlation-id', req.correlationId);
  next();
}

export function requestLogger(req, res, next) {
  const start = Date.now();
  res.on('finish', () => {
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      method: req.method,
      path: req.path,
      status: res.statusCode,
      durationMs: Date.now() - start,
      correlationId: req.correlationId,
    }));
  });
  next();
}

export function errorHandler(err, req, res, next) {
  console.error(JSON.stringify({
    timestamp: new Date().toISOString(),
    error: err.message,
    path: req.path,
    correlationId: req.correlationId,
  }));
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
    correlationId: req.correlationId,
  });
}
