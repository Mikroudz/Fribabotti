import { EditGroup } from "#/Groups/GroupEdit";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/groups/new")({
    component: RouteComponent,
});

function RouteComponent() {
    return <EditGroup />;
}
