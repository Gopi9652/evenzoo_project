# Evenzoo — Data Breach Response Runbook

If you discover or suspect a data breach, follow these steps in order:

## 1. Contain (First Hour)
- [ ] Rotate JWT_SECRET immediately (forces all users to re-login, invalidates any stolen tokens)
- [ ] Rotate database password if the breach involves direct DB access
- [ ] Revoke and rotate Razorpay API keys if payment data may be involved
- [ ] Revoke and rotate Cloudinary/MSG91 API keys if those services are implicated
- [ ] If a specific vulnerability was exploited, deploy a fix or take the affected endpoint offline

## 2. Assess (First 24 Hours)
- [ ] Determine what data was actually accessed (check logs, query the affected tables)
- [ ] Determine how many users are affected
- [ ] Determine whether payment data, passwords, or highly sensitive fields were exposed

## 3. Notify (Within 72 Hours)
- [ ] Draft a clear, honest email to affected users explaining what happened
- [ ] Send via your email provider to all affected user email addresses
- [ ] Post an update on your Contact/About page if the breach is significant
- [ ] Research current DPDP Act 2023 reporting requirements for Indian data protection authority notification

## 4. Remediate
- [ ] Fix the root cause completely, not just the symptom
- [ ] Force password resets for affected accounts if passwords may have been exposed
- [ ] Document what happened and what changed, for your own future reference

## Key Contacts / Resources
- Razorpay support: [their support URL]
- Railway support: [their support URL]
- Your own emergency contact list: [fill in]