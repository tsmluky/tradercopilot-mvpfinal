export const formatPrice = (price: number | undefined | null): string => {
    if (price === undefined || price === null) return '-';

    // High value (BTC, YFI) -> 2 decimals
    if (price >= 1000) return price.toFixed(2);

    // Mid value (ETH, SOL) -> 2 decimals
    if (price >= 1.0) return price.toFixed(2);

    // Low value (DOGE, XRP) -> 4 decimals
    if (price >= 0.01) return price.toFixed(4);

    // Micro value (PEPE, SHIB) -> 6-8 decimals
    if (price < 0.01) return price.toFixed(6);

    return price.toString();
};
