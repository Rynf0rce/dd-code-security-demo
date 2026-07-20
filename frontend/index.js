/**
 * GSEPS 설비 점검 대시보드 (Datadog Code Security 데모용)
 *
 * 주의: 이 파일은 의도적으로 취약하게 작성되었습니다.
 *       Datadog SAST(javascript-security) 탐지 시연 외의 목적으로 사용하지 마십시오.
 */

const express = require('express');
const { exec } = require('child_process');
const crypto = require('crypto');
const _ = require('lodash');

const app = express();

// SAST: 하드코딩된 API 키
const DASHBOARD_API_KEY = 'gseps-dash-4f19a8c2b7e04d5390af16c8de72b3a1';

// SAST: eval 사용 (사용자 입력 기반)
app.get('/api/calc', (req, res) => {
  const expr = req.query.expr;
  res.json({ result: eval(expr) });
});

// SAST: command injection (child_process.exec + 사용자 입력)
app.get('/api/tail', (req, res) => {
  const file = req.query.file;
  exec('tail -n 100 /var/log/scada/' + file, (err, stdout) => {
    res.type('text/plain').send(stdout);
  });
});

// SAST: 취약한 해시 알고리즘(SHA1)
app.get('/api/etag', (req, res) => {
  const tag = crypto.createHash('sha1').update(req.query.body || '').digest('hex');
  res.json({ etag: tag });
});

// SAST: 반사형 XSS (사용자 입력을 이스케이프 없이 HTML로 반환)
app.get('/api/greet', (req, res) => {
  res.send('<h1>안녕하세요 ' + req.query.name + '님</h1>');
});

// SAST: 예측 가능한 난수를 보안 토큰에 사용
function issueSessionToken() {
  return Math.random().toString(36).slice(2);
}

// SAST: prototype pollution 유발 가능한 lodash.merge 사용
app.post('/api/settings', express.json(), (req, res) => {
  const defaults = { theme: 'light', refresh: 30 };
  res.json(_.merge(defaults, req.body));
});

app.listen(3000, '0.0.0.0', () => {
  console.log('dashboard listening on 3000, key=' + DASHBOARD_API_KEY);
  console.log('session token sample: ' + issueSessionToken());
});
