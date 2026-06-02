import { courseGraphQueryOptions } from "#/hooks/GameSessionHooks";
import { Box, Link as MuiLink, Tab, Tabs, Typography } from "@mui/material";
import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute, createLink, Outlet, useMatchRoute } from "@tanstack/react-router";
import { forwardRef } from "react";
import { Route as RouteScore } from "#/routes/course.$courseId.graphs.score";
import { Route as RouteThrow } from "#/routes/course.$courseId.graphs.throws";

export const Route = createFileRoute("/course/$courseId/graphs")({
    component: RouteComponent,
    loader: ({ context: { queryClient }, params: { courseId } }) =>
        queryClient.ensureQueryData(courseGraphQueryOptions(courseId)),
});

const RouterLink = createLink(
    forwardRef((props, ref) => {
        return <MuiLink ref={ref} {...props} />;
    }),
);

function MuiNavTabs({ tabs, ...tabsProps }) {
    const matchRoute = useMatchRoute();

    // Find active tab based on current route
    const activeTab = tabs.find((tab) => matchRoute({ to: tab.to, fuzzy: true }))?.value || false;

    return (
        <Tabs
            value={activeTab}
            {...tabsProps}
            sx={{
                "& .MuiTabs-indicator": {
                    backgroundColor: "secondary.main",
                },
                mb: 1,
            }}
        >
            {tabs.map((tab) => (
                <Tab
                    replace
                    key={tab.value}
                    label={tab.label}
                    value={tab.value}
                    icon={tab.icon}
                    component={RouterLink}
                    to={tab.to}
                    sx={{
                        "&.Mui-selected": {
                            fontWeight: "bold",
                            color: "secondary.main",
                        },
                    }}
                />
            ))}
        </Tabs>
    );
}

const tabs = [
    { to: RouteScore.to, label: "Scores Stats", icon: null, value: "score" },
    { to: RouteThrow.to, label: "Throw Stats", icon: null, value: "throws" },
];

function RouteComponent() {
    const { courseId } = Route.useParams();

    const { data: course } = useSuspenseQuery(courseGraphQueryOptions(courseId));
    return (
        <Box sx={{ p: 1, width: "100%", minWidth: "300px" }}>
            <Typography variant="h5">{course?.name}</Typography>
            <MuiNavTabs tabs={tabs} />
            <Outlet />
        </Box>
    );
}
