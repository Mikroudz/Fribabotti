import MuiTheme from "./context/ThemeContext";
import { RouterProvider } from "@tanstack/react-router";
import { getRouter } from "./router";
import { QueryClientProvider } from "@tanstack/react-query";
import { AppBarPortalProvider } from "./context/AppBarPortal";

const router = getRouter();

const queryClient = router.options.context.queryClient;

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <MuiTheme>
                <AppBarPortalProvider>
                    <RouterProvider router={router} />
                </AppBarPortalProvider>
            </MuiTheme>
        </QueryClientProvider>
    );
}

export default App;
