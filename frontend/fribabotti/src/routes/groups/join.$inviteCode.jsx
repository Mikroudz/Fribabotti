import { useGetGroupInvite } from "#/hooks/ProfileHooks";
import { joinGroup } from "#/utils/api";
import { Box, Button, Typography } from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { createFileRoute, useNavigate, useParams } from "@tanstack/react-router";
import { Route as GroupRoute } from "./$groupId.index";

export const Route = createFileRoute("/groups/join/$inviteCode")({
    component: RouteComponent,
});

function RouteComponent() {
    const params = useParams({ strict: false });
    const { inviteCode } = params;
    const { data: group } = useGetGroupInvite(inviteCode);
    const navigate = useNavigate();

    const { mutate } = useMutation({
        mutationFn: () => joinGroup(inviteCode),
        onSuccess: (data) => {
            const group_id = data?.id;
            navigate({ to: GroupRoute.to, params: { groupId: group_id } });
        },
    });

    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                width: "auto",
                justifyContent: "center",
                alignItems: "center",
                height: "100%",
            }}
        >
            <Typography>Join Group</Typography>
            <Typography>{group?.name}</Typography>
            <Button variant="contained" sx={{ bgcolor: "secondary.main", mt: 2 }} onClick={mutate}>
                Join
            </Button>
        </Box>
    );
}
