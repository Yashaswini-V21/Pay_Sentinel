# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.x   | ✅ Active |
| 1.x     | ❌ EOL    |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Email**: paysentinel.security@proton.me
2. **Do NOT** open a public GitHub issue for security vulnerabilities
3. Include steps to reproduce and potential impact
4. We will acknowledge within 48 hours and provide a fix within 7 days

## Security Measures Implemented

### Input Validation
- All merchant names sanitized via `bleach` (HTML tag stripping)
- Regex validation for alphanumeric + Unicode (Kannada/Hindi/Tamil/Telugu)
- Maximum input lengths enforced (merchant name: 200 chars, question: 300 chars)
- File uploads limited to 10MB with extension whitelist (.csv, .xlsx, .xls)
- Negative and extreme amounts (>₹10cr) rejected at validation layer

### API Security
- Rate limiting: 30 requests/minute per IP (sliding window)
- Optional API key authentication via `PAYSENTINEL_API_KEY` env var
- Request ID tracing via `ContextVar` for audit logging
- No sensitive data in error responses

### HTTP Security Headers
- `Content-Security-Policy`: script-src 'self' + CDN whitelist
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `X-XSS-Protection`: 1; mode=block
- `Referrer-Policy`: strict-origin-when-cross-origin
- `Strict-Transport-Security`: max-age=31536000 (when behind HTTPS proxy)
- Server header stripped in production

### Infrastructure
- Docker: non-root user (`paysentinel`, UID 1000)
- Gunicorn: max-requests 1000 with jitter (worker recycling)
- Dependencies pinned to exact versions in `requirements.txt`
- No secrets committed to repository (`.env` in `.gitignore`)
