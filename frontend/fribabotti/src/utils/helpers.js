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

export function getShortDistanceArr(val1, val2, decimalplaces = 1) {
    return getShortDistance(val1[0], val1[1], val2[0], val2[1], decimalplaces);
}

export function formatSecondsToTime(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);

    // Convert to strings and pad with leading zeros if they are single digits

    return `${hours}h ${minutes}m`;
}

export function getScoreEmoji(score, par) {
    if (score === 1) return "🎯"; // Ace!
    if (score === 0) return "⬛"; // no score recorded

    const diff = score - par;
    if (diff <= -2) return "🟨"; // Eagle or better
    if (diff === -1) return "🟩"; // Birdie
    if (diff === 0) return "⬜"; // Par
    if (diff === 1) return "🟦"; // Bogey
    return "🟧"; // Double Bogey or worse
}

function formatRelativeScore(score, par) {
    const diff = score - par;
    if (diff === 0) return "E";
    return diff > 0 ? `+${diff}` : diff;
}

function generateCardRows(holes) {
    // 9 holes per row
    let text = "";
    for (let i = 0; i < holes.length; i += 9) {
        const chunk = holes.slice(i, i + 9);
        const rowScore = chunk.reduce((sum, h) => sum + h.score, 0);
        const rowPar = chunk.reduce((sum, h) => sum + h.par, 0);
        const rowEmojis = chunk.map((h) => getScoreEmoji(h.score, h.par)).join("");
        const rowTitle = i < 9 ? `${i + 1} - ${i + 9} : ` : `${i + 1}-${i + 9}:`;
        text += `${rowTitle}${rowEmojis} (${formatRelativeScore(rowScore, rowPar)})\n`;
    }
    return text;
}

function generateScoreRow(score) {
    return `🏆 Score: ${formatRelativeScore(score?.total_score, score?.par)} (${score?.total_score}) ${score?.username}\n`;
}

export function generateShareableScorecard(session) {
    const {
        course: { name },
        started_at,
        user_score,
        playtime,
    } = session;

    // 1. Format the Header
    let text = `🌲 ${name}\n`;
    text += `🗓️ ${new Date(started_at).toLocaleDateString()} • ⏱️ ${formatSecondsToTime(playtime)}\n`;
    // user score first
    text += generateScoreRow(session?.user_score);
    // rest next
    text += session?.other_scores.reduce((acc, val) => (acc += generateScoreRow(val)), "");
    text += "\n";

    text += generateCardRows(user_score?.scores);

    return text;
}
