#!/usr/bin/env node
/**
 * OFF AI backend (JavaScript / Node.js).
 * Provides:
 * - GET /api/submissions
 * - POST /api/submissions
 * - POST /api/save-html
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const DATA_FILE = path.join(ROOT, 'submissions.json');
const INDEX_FILE = path.join(ROOT, 'index.html');

function readRows() {
  if (!fs.existsSync(DATA_FILE)) return [];
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
  } catch {
    return [];
  }
}

function writeRows(rows) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(rows, null, 2));
}

const server = http.createServer((req, res) => {
  const setHeaders = (status = 200, type = 'application/json') => {
    res.statusCode = status;
    res.setHeader('Content-Type', type);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  };

  if (req.method === 'OPTIONS') {
    setHeaders(204);
    return res.end();
  }

  if (req.method === 'GET' && req.url === '/api/submissions') {
    setHeaders();
    return res.end(JSON.stringify(readRows()));
  }

  if (req.method === 'POST' && (req.url === '/api/submissions' || req.url === '/api/save-html')) {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      const payload = body ? JSON.parse(body) : {};

      if (req.url === '/api/submissions') {
        const rows = readRows();
        rows.push(payload);
        writeRows(rows);
        setHeaders();
        return res.end(JSON.stringify({ ok: true, count: rows.length }));
      }

      fs.writeFileSync(INDEX_FILE, payload.content || '', 'utf-8');
      setHeaders();
      return res.end(JSON.stringify({ ok: true, saved: 'index.html' }));
    });
    return;
  }

  setHeaders(404);
  res.end(JSON.stringify({ error: 'Not found' }));
});

const PORT = process.env.PORT || 8001;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`JavaScript backend running at http://0.0.0.0:${PORT}`);
});
