# Pattern: Consent Management

Use when consent is the lawful basis. The example is illustrative; adapt to your storage and audit requirements.

## Consent Data Model + Service (Example)

```javascript
// Consent data model
const consentSchema = {
  userId: String,
  consents: [{
    purpose: String,         // 'marketing', 'analytics', etc.
    granted: Boolean,
    timestamp: Date,
    source: String,          // 'web_form', 'api', etc.
    version: String,         // Privacy policy version
    ipAddress: String,       // For proof
    userAgent: String        // For proof
  }],
  auditLog: [{
    action: String,          // 'granted', 'withdrawn', 'updated'
    purpose: String,
    timestamp: Date,
    source: String
  }]
};

// Consent service
class ConsentManager {
  async recordConsent(userId, purpose, granted, metadata) {
    const consent = {
      purpose,
      granted,
      timestamp: new Date(),
      source: metadata.source,
      version: await this.getCurrentPolicyVersion(),
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent
    };

    // Store consent
    await this.db.consents.updateOne(
      { userId },
      {
        $push: {
          consents: consent,
          auditLog: {
            action: granted ? 'granted' : 'withdrawn',
            purpose,
            timestamp: consent.timestamp,
            source: metadata.source
          }
        }
      },
      { upsert: true }
    );

    // Emit event for downstream systems
    await this.eventBus.emit('consent.changed', {
      userId,
      purpose,
      granted,
      timestamp: consent.timestamp
    });
  }

  async hasConsent(userId, purpose) {
    const record = await this.db.consents.findOne({ userId });
    if (!record) return false;

    const latestConsent = record.consents
      .filter(c => c.purpose === purpose)
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    return latestConsent?.granted === true;
  }

  async getConsentHistory(userId) {
    const record = await this.db.consents.findOne({ userId });
    return record?.auditLog || [];
  }
}
```

## Consent UI Example

```html
<div class="consent-banner" role="dialog" aria-labelledby="consent-title">
  <h2 id="consent-title">Cookie Preferences</h2>

  <p>We use cookies to improve your experience. Select your preferences below.</p>

  <form id="consent-form">
    <div class="consent-category">
      <input type="checkbox" id="necessary" checked disabled>
      <label for="necessary">
        <strong>Necessary</strong>
        <span>Required for the website to function. Cannot be disabled.</span>
      </label>
    </div>

    <div class="consent-category">
      <input type="checkbox" id="analytics" name="analytics">
      <label for="analytics">
        <strong>Analytics</strong>
        <span>Help us understand how you use our site.</span>
      </label>
    </div>

    <div class="consent-category">
      <input type="checkbox" id="marketing" name="marketing">
      <label for="marketing">
        <strong>Marketing</strong>
        <span>Personalized ads based on your interests.</span>
      </label>
    </div>

    <div class="consent-actions">
      <button type="button" id="accept-all">Accept All</button>
      <button type="button" id="reject-all">Reject All</button>
      <button type="submit">Save Preferences</button>
    </div>

    <p class="consent-links">
      <a href="/privacy-policy">Privacy Policy</a> |
      <a href="/cookie-policy">Cookie Policy</a>
    </p>
  </form>
</div>
```
