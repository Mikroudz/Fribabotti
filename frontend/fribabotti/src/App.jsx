import { useEffect } from "react";

import MuiTheme from "./context/ThemeContext";
import { CssBaseline } from "@mui/material";
import { RouterProvider } from "@tanstack/react-router";
import { getRouter } from "./router";
import { QueryClientProvider } from "@tanstack/react-query";

const router = getRouter();

const queryClient = router.options.context.queryClient;

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <MuiTheme>
                <RouterProvider router={router} />
            </MuiTheme>
        </QueryClientProvider>
    );
}

export default App;
