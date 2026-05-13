import { Alert, Snackbar } from "@mui/material";
import { createContext, useCallback, useContext, useMemo, useState } from "react";

const SnackbarContext = createContext({});

const SNACK_TYPES = { success: "success", error: "error", info: "info" };

export function SnackbarContextProvider({ children }) {
    const [snack, setSnack] = useState({ message: "", type: SNACK_TYPES.info, open: false });
    const [open, setOpen] = useState(false);

    const handleClose = () => {
        setOpen(false);
    };

    const showSnack = useCallback((text, type = "") => {
        const typeExists = type in SNACK_TYPES ? type : SNACK_TYPES.info;
        setSnack({ message: text, type: typeExists });
        setOpen(true);
    }, []);

    const contextState = useMemo(() => {
        return { showSnack };
    }, [showSnack]);

    return (
        <SnackbarContext.Provider value={contextState}>
            {children}
            <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
                <Alert
                    onClose={handleClose}
                    severity={snack?.type || "success"}
                    variant="filled"
                    sx={{ width: "100%" }}
                >
                    {snack.message || ""}
                </Alert>
            </Snackbar>
        </SnackbarContext.Provider>
    );
}

export const useSnackbar = () => useContext(SnackbarContext);
