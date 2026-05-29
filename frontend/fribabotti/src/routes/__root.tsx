import { Link, Outlet, Scripts, createRootRouteWithContext } from "@tanstack/react-router";
import { TanStackRouterDevtoolsPanel } from "@tanstack/react-router-devtools";
import { TanStackDevtools } from "@tanstack/react-devtools";

import TanStackQueryDevtools from "../integrations/tanstack-query/devtools";

import { BottomNavigation, BottomNavigationAction, Box, CssBaseline, Paper} from "@mui/material";
import { Person } from '@mui/icons-material';

import "@fontsource-variable/lexend/wght.css";
import type { QueryClient } from "@tanstack/react-query";
import { Route as CourseRoute } from "./course.index"
import { Route as ProfileRoute } from "./profile/index"

import { HeaderBar } from "#/components/HeaderBar";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import GolfCourseIcon from '@mui/icons-material/GolfCourse';


interface MyRouterContext {
  queryClient: QueryClient,
  authHandlerRef: { current: (() => void) | null }
}


export const Route = createRootRouteWithContext<MyRouterContext>()({
    component: RootDocument,
});

function RootDocument() {
    return (
        <>
            <CssBaseline />
            
            <Box sx={{height: "100dvh", width: "100vw", display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>

                <HeaderBar />
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
                <Paper sx={{ flexShrink: 0, zIndex: 1300}} elevation={3}>
                    <BottomNavigation showLabels>
                    <BottomNavigationAction label="Game" icon={<PlayArrowIcon />} component={Link} to={"/"} />
                    <BottomNavigationAction label="Courses" icon={<GolfCourseIcon />} component={Link} to={CourseRoute.to} />
                    <BottomNavigationAction label="Profile" icon={<Person />} component={Link} to={ProfileRoute.to} />
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
        </>
    );
}
