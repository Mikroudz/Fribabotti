import { Box } from "@mui/material";
import { createContext, useContext, useState } from "react";
import { Portal } from "@mui/material";

const AppBarPortalContext = createContext(null);

export function AppBarPortalProvider({ children }) {
    const [container, setContainer] = useState(null);
    return (
        <AppBarPortalContext.Provider value={{ container, setContainer }}>
            {children}
        </AppBarPortalContext.Provider>
    );
}

export function AppBarPortalSlot() {
    const { setContainer } = useAppBarPortal();
    return <Box ref={setContainer} sx={{ display: "flex", gap: "8px" }} />;
}

export function AppBarAction({ children }) {
    const { container } = useAppBarPortal();
    if (!container) return null;
    return <Portal container={container}>{children}</Portal>;
}

export const useAppBarPortal = () => useContext(AppBarPortalContext);
