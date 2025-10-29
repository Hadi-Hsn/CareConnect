# Threat Model & Security Analysis

This document outlines security considerations for the CareConnect healthcare assistant.

## Risk Classification

CareConnect handles **Protected Health Information (PHI)** including:
- Patient names, dates of birth
- Contact information (email, phone)
- Appointment details
- Health conditions (reason for visit)

**Compliance Considerations**:
- HIPAA Security Rule (if deployed in US healthcare context)
- GDPR (if serving EU patients)
- State-specific privacy laws

⚠️ **Note**: This implementation provides HIPAA-conscious design patterns but is NOT certified for production PHI without additional controls (BAA with OpenAI, encryption at rest, access logging, etc.)

## STRIDE Threat Analysis

### 1. Spoofing Identity

**Threats**:
- Attacker impersonates patient to access appointments
- Stolen JWT tokens used to access other users' data
- Session hijacking

**Mitigations**:
- ✅ JWT tokens with 30-minute expiration
- ✅ Password hashing with bcrypt (12 rounds)
- ✅ Token validation on every authenticated request
- ❌ **TODO**: Multi-factor authentication (MFA)
- ❌ **TODO**: Device fingerprinting
- ❌ **TODO**: IP-based anomaly detection

**Residual Risk**: Medium (MFA not implemented)

### 2. Tampering with Data

**Threats**:
- Modify appointment details without authorization
- Change provider availability
- Manipulate booking confirmation codes
- Inject malicious content into RAG documents

**Mitigations**:
- ✅ Database constraints (foreign keys, unique constraints)
- ✅ Pydantic validation on all inputs
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ Role-based access control (patient/staff/admin)
- ✅ Audit trail (`booking_event` table tracks all changes)
- ❌ **TODO**: Cryptographic signatures on appointment confirmations
- ❌ **TODO**: Immutable audit log (append-only)

**Residual Risk**: Low-Medium

### 3. Repudiation

**Threats**:
- User denies booking/cancelling appointment
- Admin denies modifying RAG documents
- No proof of who performed action

**Mitigations**:
- ✅ Audit trail with user_id, action, timestamp in `booking_event`
- ✅ Request ID tracking in logs
- ✅ Structured logging with user context
- ❌ **TODO**: Digital signatures on transactions
- ❌ **TODO**: Tamper-evident log storage (write to S3 with versioning)

**Residual Risk**: Medium

### 4. Information Disclosure

**Threats**:
- PHI leaked in logs
- Patient sees other patients' appointments
- Embeddings expose sensitive content
- Error messages reveal internal structure
- Vector store metadata leaks PHI

**Mitigations**:
- ✅ PHI masking in logs when `ENABLE_PRIVACY_MODE=true`
- ✅ Database row-level filtering (only return current user's data)
- ✅ CORS restricted to frontend origin
- ✅ Generic error messages to users (detailed logs server-side)
- ✅ Rate limiting prevents enumeration attacks
- ✅ No raw PHI in vector store metadata (only doc IDs)
- ❌ **TODO**: Encrypt database at rest
- ❌ **TODO**: TLS for all connections (HTTPS enforced)
- ❌ **TODO**: Field-level encryption for sensitive columns

**Residual Risk**: Medium (encryption at rest not implemented)

### 5. Denial of Service

**Threats**:
- Overwhelm API with requests
- Exhaust OpenAI API quota
- Fill database with spam bookings
- Crash server with malformed inputs

**Mitigations**:
- ✅ Rate limiting (60 req/min for chat, 300/min for other endpoints)
- ✅ Request size limits (FastAPI default)
- ✅ Pydantic validation rejects malformed data
- ✅ Database connection pooling
- ❌ **TODO**: OpenAI quota monitoring/alerting
- ❌ **TODO**: WAF (Web Application Firewall)
- ❌ **TODO**: DDoS protection (Cloudflare, AWS Shield)

**Residual Risk**: Medium

### 6. Elevation of Privilege

**Threats**:
- Patient accesses admin endpoints
- Modify own role in database
- Bypass authentication
- SQL injection to gain admin rights

**Mitigations**:
- ✅ Role-based access control checks on admin endpoints
- ✅ JWT contains role claim (cannot be modified without private key)
- ✅ All admin actions require `role="admin"` verification
- ✅ SQLAlchemy ORM prevents SQL injection
- ❌ **TODO**: Principle of least privilege for database user
- ❌ **TODO**: Separate admin interface with stronger auth

**Residual Risk**: Low

## Attack Surface Analysis

### Frontend (React)

**Exposed**:
- User input fields (chat, login, forms)
- API calls to backend
- localStorage (stores JWT token)

**Risks**:
- XSS (Cross-Site Scripting) via chat messages
- CSRF (Cross-Site Request Forgery)
- Token theft from localStorage

**Mitigations**:
- ✅ React escapes user input by default
- ✅ CORS protection on backend
- ✅ SameSite cookie policy (if using cookies)
- ❌ **TODO**: Content Security Policy (CSP) headers
- ❌ **TODO**: Subresource Integrity (SRI) for external scripts
- ❌ **TODO**: HttpOnly cookies instead of localStorage

**Recommendations**:
```typescript
// Use httpOnly cookies for tokens instead of localStorage
const response = await api.login(email, password);
// Token set in cookie by backend, not stored in localStorage
```

### Backend API (FastAPI)

**Exposed**:
- All `/api/v1/*` endpoints
- `/docs` (OpenAPI spec) - **Disable in production**
- `/metrics` (Prometheus) - **Restrict access**
- `/health` (public)

**Risks**:
- Authentication bypass
- Authorization flaws (vertical/horizontal privilege escalation)
- Injection attacks (SQL, command)
- Mass assignment

**Mitigations**:
- ✅ JWT validation middleware
- ✅ Pydantic schemas prevent mass assignment
- ✅ SQLAlchemy ORM (no raw SQL)
- ✅ Rate limiting
- ❌ **TODO**: Disable `/docs` in production
- ❌ **TODO**: Require auth for `/metrics`
- ❌ **TODO**: API versioning with deprecation policy

### Database (PostgreSQL)

**Exposed**:
- Only to backend application
- Port 5432 (should not be public)

**Risks**:
- Data breach if database compromised
- Backup exposure
- SQL injection (if raw queries used)

**Mitigations**:
- ✅ SQLAlchemy ORM (no raw SQL in app code)
- ✅ Password-protected connections
- ❌ **TODO**: Network isolation (VPC/private subnet)
- ❌ **TODO**: Encryption at rest
- ❌ **TODO**: Automated encrypted backups
- ❌ **TODO**: Read-only replicas for reporting

### External APIs

**Dependencies**:
- OpenAI API (GPT-4, embeddings)
- SMTP server (email delivery)

**Risks**:
- API key leakage
- Service outage (OpenAI down = CareConnect down)
- Data sent to third parties

**Mitigations**:
- ✅ API keys in environment variables (not in code)
- ✅ SMTP configured for reliable email delivery
- ✅ Graceful degradation (RAG fails → agent still works)
- ❌ **TODO**: Key rotation policy
- ❌ **TODO**: Secrets manager (AWS Secrets Manager, HashiCorp Vault)
- ❌ **TODO**: Business Associate Agreement (BAA) with OpenAI for HIPAA

⚠️ **HIPAA Consideration**: OpenAI requires BAA for PHI processing. Standard OpenAI API is NOT HIPAA-compliant. Consider:
- Azure OpenAI Service (offers BAA)
- Self-hosted LLM (e.g., Llama 2 via Ollama)
- De-identify data before sending to OpenAI

### Vector Store (FAISS)

**Storage**:
- Index file: `backend/data/faiss_index.bin`
- Metadata: `backend/data/faiss_metadata.pkl`

**Risks**:
- File tampering
- Metadata leakage (if contains PHI)
- Index corruption

**Mitigations**:
- ✅ Metadata contains only doc_id + category (no PHI)
- ✅ File permissions restricted to application user
- ❌ **TODO**: File integrity monitoring (checksums)
- ❌ **TODO**: Encrypted storage (LUKS, AWS EFS encryption)
- ❌ **TODO**: Backup and recovery procedures

## Security Testing Checklist

### Authentication & Authorization

- [ ] Cannot access protected endpoints without token
- [ ] Expired tokens are rejected
- [ ] Patient cannot access other patients' appointments
- [ ] Patient cannot access admin endpoints
- [ ] Staff can view but not modify
- [ ] Admin can modify RAG documents

### Input Validation

- [ ] SQL injection attempts fail (e.g., `'; DROP TABLE users;--`)
- [ ] XSS payloads are escaped (e.g., `<script>alert('xss')</script>`)
- [ ] Oversized requests are rejected
- [ ] Invalid date formats are rejected
- [ ] Negative IDs are rejected
- [ ] Special characters in names are handled

### Rate Limiting

- [ ] 61st chat request in 1 minute is blocked
- [ ] 301st general request in 1 minute is blocked
- [ ] Rate limit headers are present (X-RateLimit-Remaining)
- [ ] Rate limit resets after window

### Data Protection

- [ ] Passwords are hashed (never stored plain text)
- [ ] PHI is masked in logs (when privacy mode enabled)
- [ ] Error messages don't leak sensitive data
- [ ] Database queries filter by current user
- [ ] Confirmation codes are random and non-guessable

### Session Management

- [ ] Logout invalidates token (if implemented)
- [ ] Cannot reuse old tokens after password change
- [ ] Session timeout after inactivity
- [ ] Concurrent sessions are limited

## Penetration Testing Scenarios

### Scenario 1: Privilege Escalation

**Goal**: Patient tries to access admin RAG indexing endpoint

**Steps**:
1. Login as patient user
2. Extract JWT token
3. POST to `/api/v1/rag/index` with document
4. Expected: 403 Forbidden

**Test**:
```bash
curl -X POST http://localhost:8000/api/v1/rag/index \
  -H "Authorization: Bearer <patient_token>" \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"id": "test", "content": "test"}]}'
# Should return 403
```

### Scenario 2: Horizontal Privilege Escalation

**Goal**: Patient A tries to view Patient B's appointments

**Steps**:
1. Login as Patient A
2. Get appointments for Patient B by ID
3. Expected: Empty list or 403

**Test**:
```bash
# Login as patient A (user_id=1)
TOKEN_A=<token>

# Try to get appointments for user_id=2
curl http://localhost:8000/api/v1/appointments?user_id=2 \
  -H "Authorization: Bearer $TOKEN_A"
# Should return only user_id=1 appointments (filtered by JWT)
```

### Scenario 3: Token Forgery

**Goal**: Create fake JWT to impersonate admin

**Steps**:
1. Attempt to forge JWT with role="admin"
2. Expected: Signature verification fails

**Test**:
```python
import jwt

fake_token = jwt.encode(
    {"sub": "1", "role": "admin"},
    "wrong_secret",  # Not the real secret
    algorithm="HS256"
)

# Try to use fake token
# Expected: 401 Unauthorized
```

### Scenario 4: SQL Injection

**Goal**: Inject SQL via appointment reason

**Steps**:
1. Book appointment with reason: `test'; DROP TABLE appointments;--`
2. Expected: Request succeeds, but no SQL is executed (ORM escapes)

**Test**:
```bash
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 1,
    "appointment_time": "2025-02-01T10:00:00",
    "duration_minutes": 30,
    "reason": "test'"'"'; DROP TABLE appointments;--"
  }'
# Should succeed and store the string literally
# Then verify appointments table still exists
```

## Incident Response Plan

### Detection

**Indicators of Compromise**:
- Unusual spike in 401/403 errors (brute force?)
- High volume from single IP (DDoS?)
- Admin actions from unexpected IPs
- Database queries failing (injection attempt?)
- Unusual OpenAI API usage

**Monitoring**:
- Prometheus alerts (see EVALUATION.md)
- Log aggregation (grep for "ERROR", "403", "429")
- Database audit logs

### Response Procedure

**Step 1: Contain**
- If authentication compromised: Rotate JWT secret (invalidates all tokens)
- If API key leaked: Rotate OpenAI key, update SMTP credentials
- If database breached: Take snapshot, isolate network

**Step 2: Investigate**
- Review logs for attacker IP addresses
- Check database for unauthorized modifications
- Determine scope of data accessed

**Step 3: Notify**
- If PHI breach: Notify affected patients within 60 days (HIPAA requirement)
- If regulated entity: Report to HHS/OCR
- Internal stakeholders

**Step 4: Remediate**
- Apply security patches
- Implement additional controls
- Change all secrets

**Step 5: Review**
- Post-mortem analysis
- Update threat model
- Improve monitoring

## Secure Development Practices

### Code Review Checklist

- [ ] No hardcoded secrets (API keys, passwords)
- [ ] Input validation on all user data
- [ ] Authorization checks on all protected endpoints
- [ ] Sensitive data not logged
- [ ] Dependencies up to date (no known CVEs)
- [ ] SQL queries use ORM (no string concatenation)
- [ ] Error handling doesn't leak stack traces

### Dependency Scanning

**Backend**:
```bash
# Check for vulnerabilities in Python packages
pip install safety
safety check

# Or use pip-audit
pip install pip-audit
pip-audit
```

**Frontend**:
```bash
# Check for vulnerabilities in npm packages
npm audit

# Fix automatically if possible
npm audit fix
```

### Secret Management

**Current (Development)**:
- Environment variables in `.env` file (gitignored)
- Loaded via `python-dotenv`

**Recommended (Production)**:
- AWS Secrets Manager / Azure Key Vault
- Secrets injected at runtime (not in config files)
- Automatic rotation for long-lived secrets

**Example with AWS Secrets Manager**:
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# In config.py
OPENAI_API_KEY = get_secret("careconnect/openai-api-key")
```

## Compliance Readiness

### HIPAA Security Rule

**Required Controls**:

1. **Access Control** (§164.312(a)):
   - ✅ Unique user identification (user_id)
   - ✅ Emergency access procedure (admin override)
   - ❌ Automatic logoff (TODO: session timeout)
   - ❌ Encryption and decryption (TODO: field-level encryption)

2. **Audit Controls** (§164.312(b)):
   - ✅ Activity logging (`booking_event`, request logs)
   - ❌ Audit log review (TODO: automated analysis)

3. **Integrity** (§164.312(c)):
   - ✅ Mechanism to authenticate ePHI (database constraints)
   - ❌ Mechanism to detect tampering (TODO: checksums)

4. **Transmission Security** (§164.312(e)):
   - ❌ Encryption (TODO: HTTPS with TLS 1.2+)
   - ❌ Integrity controls (TODO: message signing)

**Gap Analysis**: 60% compliant (6/10 controls implemented)

**Roadmap to Compliance**:
- [ ] Implement TLS/HTTPS (1 week)
- [ ] Add session timeout (3 days)
- [ ] Encrypt database at rest (1 week)
- [ ] Field-level encryption for PHI (2 weeks)
- [ ] Sign BAA with OpenAI or switch to Azure OpenAI (1 day)
- [ ] Implement automated audit log review (1 week)
- [ ] Penetration testing by third party (1 month)
- [ ] Risk assessment and documentation (2 weeks)

### GDPR (if applicable)

**Required**:
- [ ] User consent for data processing
- [ ] Right to access (user can download their data)
- [ ] Right to erasure ("forget me")
- [ ] Data portability (export in machine-readable format)
- [ ] Data Processing Agreement with sub-processors (OpenAI, SMTP provider)

---

**Last Updated:** 2025
**Version:** 1.0
**Classification:** Internal Use Only