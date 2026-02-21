// frontend/config.js
// Simple global config for the Notes API tester.

// Your API Gateway base URL (NO trailing slash)
window.NOTES_API_CONFIG = {
  apiBaseUrl: "https://ss5k5py93l.execute-api.ap-southeast-2.amazonaws.com/prod",
};

// Your Cognito Hosted UI config
window.COGNITO_CONFIG = {
  // Cognito domain (no trailing slash)
  domain: "https://ap-southeast-2xlwv5qp6j.auth.ap-southeast-2.amazoncognito.com",

  // App client ID
  clientId: "567v4db047v4jpujij7me8nb0u",

  // Where Cognito sends you back AFTER login
  // (we'll host notes.html here eventually)
  redirectUri: "https://d84l1y8p4kdic.cloudfront.net/notes.html",

  // Scopes to request
  scope: "email openid phone",
};