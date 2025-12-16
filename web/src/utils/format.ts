if (price === undefined || price === null) return '-';

const p = Number(price);
if (isNaN(p)) return '-';

// Crypto Formatting Rules
if (p >= 1000) return p.toFixed(2);       // BTC: 96,123.50
if (p >= 10) return p.toFixed(2);         // LTC: 77.95
if (p >= 1) return p.toFixed(3);          // ADA: 1.234
if (p >= 0.1) return p.toFixed(4);        // DOGE: 0.1234
if (p < 0.1) return p.toFixed(6);         // PEPE: 0.000012

return p.toString();
};
