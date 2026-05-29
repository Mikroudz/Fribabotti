import { EditGroup } from "#/Groups/GroupEdit";
import { useUserGroup } from "#/hooks/ProfileHooks";
import { createFileRoute, useParams } from "@tanstack/react-router";

export const Route = createFileRoute("/groups/$groupId/edit")({
    component: RouteComponent,
});

function RouteComponent() {
    const params = useParams({ strict: false });
    const { groupId } = params;

    const { data: group } = useUserGroup(groupId);

    return <EditGroup group={group} />;
}
