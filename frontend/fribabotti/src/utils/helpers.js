const locale = getBrowserLanguageCode();

const formatLong = new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
});

export const dateTimeNice = (date) => {
    const ret = date ? formatLong.format(new Date(date)) : "";
    return ret;
};

export function getBrowserLanguageCode() {
    if (navigator.languages != undefined) return navigator.languages[0];
    return navigator.language;
}

export function getShortDistance(lat1, lon1, lat2, lon2, decimalplaces = 1) {
    const R = 6371e3;
    const x = (((lon2 - lon1) * Math.PI) / 180) * Math.cos(((lat1 + lat2) * Math.PI) / 360);
    const y = ((lat2 - lat1) * Math.PI) / 180;
    return (Math.sqrt(x * x + y * y) * R).toFixed(decimalplaces);
}

export function formatSecondsToTime(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);

    // Convert to strings and pad with leading zeros if they are single digits

    return `${hours}h ${minutes}m`;
}
