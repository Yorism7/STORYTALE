#!/usr/bin/env node
/**
 * SSH CLI CURSOR – รันคำสั่งบน host ผ่าน extension (ให้ AI เรียกได้)
 *
 * วิธีใช้: node scripts/ssh-cli-run.js <host> <command>
 * ตัวอย่าง: node scripts/ssh-cli-run.js prod "ls -la"
 *
 * ต้องเปิด workspace (โฟลเดอร์ที่รันคำสั่งนี้อยู่) ใน Cursor และติดตั้ง extension SSH CLI CURSOR
 * Extension จะ watch ไฟล์ .cursor/ssh-cli-request.json แล้วรันคำสั่ง แล้วเขียนผลลง .cursor/ssh-cli-output.txt
 *
 * ใช้กับโปรเจกต์อื่น: รันจาก root ของโปรเจกต์นั้น (cwd = โปรเจกต์นั้น) หรือ copy ไฟล์นี้ไปไว้ในโปรเจกต์นั้น
 * ดู docs/CURSOR-AI-USAGE.md ส่วน "ใช้กับโปรเจกต์อื่น"
 */

const fs = require('fs');
const path = require('path');

const host = process.argv[2];
const command = process.argv[3];

if (!host || !command) {
  console.error('Usage: node scripts/ssh-cli-run.js <host> <command>');
  console.error('Example: node scripts/ssh-cli-run.js prod "ls -la"');
  process.exit(1);
}

const cwd = process.cwd();
const requestPath = path.join(cwd, '.cursor', 'ssh-cli-request.json');
const outputPath = path.join(cwd, '.cursor', 'ssh-cli-output.txt');
const dir = path.dirname(requestPath);

try {
  fs.mkdirSync(dir, { recursive: true });
} catch (e) {
  console.error('Cannot create .cursor directory:', e.message);
  process.exit(1);
}

try {
  if (fs.existsSync(outputPath)) fs.unlinkSync(outputPath);
} catch {}

fs.writeFileSync(requestPath, JSON.stringify({ host, command }, null, 0), 'utf8');

const timeoutMs = 60000;
const pollMs = 500;
const start = Date.now();

const poll = () => {
  if (Date.now() - start > timeoutMs) {
    console.error('[ssh-cli-run] Timeout: extension did not write output within 60s. Is Cursor open with this workspace and SSH CLI CURSOR extension enabled?');
    process.exit(1);
  }
  try {
    if (fs.existsSync(outputPath)) {
      const out = fs.readFileSync(outputPath, 'utf8');
      console.log(out);
      process.exit(0);
    }
  } catch (e) {
    console.error('[ssh-cli-run] Read output failed:', e.message);
    process.exit(1);
  }
  setTimeout(poll, pollMs);
};

setTimeout(poll, pollMs);
