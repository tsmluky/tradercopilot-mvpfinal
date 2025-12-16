export const formatPrice = (price: number | string | undefined | null): string => {
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

export const formatRelativeTime = (dateStr: string | undefined): string => {
    if (!dateStr) return '-';
    // Ensure UTC if missing Z
    const safeDate = dateStr.endsWith('Z') ? dateStr : `${dateStr}Z`;
    const date = new Date(safeDate);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    // Future handling
    if (diff < 0) return 'Just now';

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
};
