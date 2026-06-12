import { StrictMode, useEffect } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { isTelegramApp } from "./utils/telegramHelpers";
import { tgInit } from "./auth/tgInit";

function RootApp() {
    useEffect(() => {
        const appInit = async () => {
            if (await isTelegramApp()) {
                tgInit();
            }
        };
        appInit();
    }, []);

    return (
        <StrictMode>
            <App />
        </StrictMode>
    );
}

createRoot(document.getElementById("root")).render(<RootApp />);
