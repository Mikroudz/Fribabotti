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

export async function getGameSessions({ limit = null, course_id = null }) {
    const params = {};
    if (limit !== null) {
        params["limit"] = limit;
    }
    if (course_id !== null) {
        params["course_id"] = course_id;
    }
    const queryParams = new URLSearchParams(params);
    return baseFetch("/game_session?" + queryParams.toString());
}

export async function getGameSession({ queryKey }) {
    const [_key, session_id] = queryKey;
    return baseFetch(`/game_session/${session_id}`);
}

export async function createGameSession({ data, method = "POST" }) {
    const url = method !== "POST" ? `/game_session/${data.id}` : "/game_session";
    return baseFetch(url, { method: method, body: JSON.stringify(data) });
}

export async function endGameSession({ data, session_id }) {
    const { close = true } = data;
    return baseFetch(`/game_session/${session_id}/end?close=${close}`, { method: "PATCH" });
}

export async function getCourse({ queryKey }) {
    const [_key, course_id] = queryKey;
    return baseFetch(`/courses/${course_id}`);
}

export async function getCourses() {
    return baseFetch(`/courses`);
}

export async function createCourse({ data, method = "POST" }) {
    const url = ["PATCH", "DELETE"].includes(method) ? `/courses/${data.id}` : "/courses";
    return baseFetch(url, { method: method, body: JSON.stringify(data) });
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

export async function getUserGroups() {
    return baseFetch(`/groups`);
}
