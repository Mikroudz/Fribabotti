import { Outlet, Scripts, createRootRouteWithContext } from "@tanstack/react-router";
import { TanStackRouterDevtoolsPanel } from "@tanstack/react-router-devtools";
import { TanStackDevtools } from "@tanstack/react-devtools";

import TanStackQueryDevtools from "../integrations/tanstack-query/devtools";

import MuiTheme from "../context/ThemeContext";
import { AppBar, BottomNavigation, BottomNavigationAction, Box, CssBaseline, Paper, Toolbar, Typography } from "@mui/material";
import { Home, Search, Person } from '@mui/icons-material';

import "@fontsource-variable/lexend/wght.css";
import type { QueryClient } from "@tanstack/react-query";

interface MyRouterContext {
  queryClient: QueryClient,
  authHandlerRef: { current: (() => void) | null }
}


export const Route = createRootRouteWithContext<MyRouterContext>()({
    component: RootDocument,
});

function RootDocument() {
    return (
        <MuiTheme>
            <CssBaseline />
            
            <Box sx={{height: "100dvh", width: "100vw", display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>

                <AppBar position="static" sx={{ flexShrink: 0 }}>
                    <Toolbar>
                        <Typography variant="h6">Fribabotti</Typography>
                    </Toolbar>
                </AppBar>
                <Box
                    component="main"
                    sx={{
                        display: 'flex',
                        flexGrow: 1,
                        bgcolor: "background.default",
                        flexDirection: 'column', overflow: 'auto'
                    }}
                >
                    <Outlet />
                </Box>
                <Paper sx={{ flexShrink: 0, zIndex: 10 }} elevation={3}>
                    <BottomNavigation showLabels>
                    <BottomNavigationAction label="Game" icon={<Home />} />
                    <BottomNavigationAction label="Map" icon={<Search />} />
                    <BottomNavigationAction label="Profile" icon={<Person />} />
                    </BottomNavigation>
                </Paper>
                </Box>
            <TanStackDevtools
                config={{
                    position: "bottom-right",
                }}
                plugins={[
                    {
                        name: "Tanstack Router",
                        render: <TanStackRouterDevtoolsPanel />,
                    },
                    TanStackQueryDevtools,
                ]}
            />
            <Scripts />
        </MuiTheme>
    );
}
