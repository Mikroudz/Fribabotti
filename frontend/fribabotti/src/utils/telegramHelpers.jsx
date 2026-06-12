import { request2 } from "@tma.js/sdk-react";

let inTelegram = null;

export async function isTelegramApp() {
    if (inTelegram === null) {
        try {
            // Attempt to request the theme from the native Telegram wrapper
            await request2("web_app_request_theme", "theme_changed", { timeout: 150 });
            inTelegram = true;
        } catch (error) {
            inTelegram = false;
        }
    }

    return inTelegram;
}

export const TELEGRAM_AUTH_TYPES = { webapp: "TGWEBAPP", auth_widget: "TGAUTH" };

function bufferToHex(buffer) {
    return Array.from(new Uint8Array(buffer))
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
}

/*
 *   Calculates sign hash of bot authentication message for demo mode/dummy login.
 */
export async function calculateDummyHash(data) {
    const sortedKeys = Object.keys(data).sort();
    const msg = sortedKeys.map((key) => `${key}=${data[key]}`).join("\n");

    const encoder = new TextEncoder();
    const msg_encoded = encoder.encode(msg);
    const key_encoded = encoder.encode(import.meta.env.VITE_DEMO_MODE_BOT_AUTH_KEY);
    const tokenKey = await window.crypto.subtle.digest("SHA-256", key_encoded);
    const hmacKey = await window.crypto.subtle.importKey(
        "raw",
        tokenKey,
        {
            name: "HMAC",
            hash: "SHA-256",
        },
        true,
        ["sign"],
    );

    const signature = await window.crypto.subtle.sign("HMAC", hmacKey, msg_encoded);
    const ret = bufferToHex(signature);
    return ret;
}
