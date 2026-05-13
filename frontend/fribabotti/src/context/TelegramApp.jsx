import { createContext, useContext, useEffect, useState } from "react";
import { isTelegramApp } from "../utils/telegramHelpers";

const TelegramAppContext = createContext({});

export function TelegramAppProvider({ children }) {
    const [value, setValue] = useState({ isTgApp: isTelegramApp() });

    useEffect(() => {
        setValue((prev) => ({ ...prev, isTgApp: isTelegramApp() }));
    }, []);

    return <TelegramAppContext.Provider value={value}>{children}</TelegramAppContext.Provider>;
}

export const useTelegramApp = () => useContext(TelegramAppContext);
