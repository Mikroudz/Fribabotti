import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/course")({
    component: RouteComponent,
});

function RouteComponent() {
    return <Outlet />;
}
