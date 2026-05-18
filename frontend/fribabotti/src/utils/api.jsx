async function baseFetch(endpoint, options = {}) {
    // new URL required for testing.
    const url = new URL(`${import.meta.env.VITE_API_URL}${endpoint}`, import.meta.url);
    const defaults = {
        mode: "cors",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
        credentials: "include",
    };
    const res = await fetch(url, { ...defaults, ...options });
    if (!res.ok) {
        throw res;
    }
    return res.json();
}

export async function telegramAuth(data) {
    return baseFetch("/auth/telegram", { method: "POST", body: JSON.stringify(data) });
}

export async function signOut() {
    return baseFetch("/auth/logout", { method: "POST" });
}

export async function refreshToken() {
    return baseFetch("/auth/refresh", { method: "POST" });
}

export async function getUser() {
    return baseFetch("/user");
}

export async function getGameSessions() {
    return baseFetch("/game_session");
}

export async function getGameSession({ queryKey }) {
    const [_key, session_id] = queryKey;
    return baseFetch(`/game_session/${session_id}`);
}

export async function createGameSession({ data, method = "POST" }) {
    const url = method !== "POST" ? `/game_session/${data.id}` : "/game_session";
    return baseFetch(url, { method: method, body: JSON.stringify(data) });
}

export async function getTrack(track_id) {
    return baseFetch(`/tracks/${track_id}`);
}

export async function getTracks() {
    return baseFetch(`/tracks`);
}

export async function createThrow({ data, method = "POST" }) {
    const url = method === "DELETE" ? `/scores/throw/${data.id}` : "/scores/throw";
    return baseFetch(url, { method: method, body: JSON.stringify(data) });
}

export async function deleteThrow(throw_id) {
    return baseFetch(`/scores/throw/${throw_id}`, { method: "DELETE" });
}

export async function updateScore({ data, method = "POST" }) {
    return baseFetch(`/scores`, { method: method, body: JSON.stringify(data) });
}
