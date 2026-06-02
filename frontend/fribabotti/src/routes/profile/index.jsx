import { useUser } from "#/auth/UserHooks";
import { StyledListItem, StyledListItemButton } from "#/components/List";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { GroupList } from "#/Groups/GroupList";
import { getDeviceSessions } from "#/utils/api";
import { dateTimeNice } from "#/utils/helpers";
import { Avatar, Box, lighten, List, ListItemText, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/profile/")({
    component: RouteComponent,
    beforeLoad: () => ({
        headerTitle: "Profile",
    }),
});

export function InfoBox({ title, value }) {
    return (
        <StyledAnyContentBox
            sx={{
                display: "flex",
                flexDirection: "column",
                pl: 2,
                pr: 2,
                pb: 0.5,
                pt: 0.5,
                mt: 0,
                border: 0,
                bgcolor: (theme) => lighten(theme.palette.background.paper, 0.05),
            }}
        >
            <Typography component="span" variant="subtitle1">
                {title}
            </Typography>
            <Typography component="span" variant="h5">
                {value}
            </Typography>
        </StyledAnyContentBox>
    );
}

function ProfileInfo() {
    const { user } = useUser();
    return (
        <StyledAnyContentBox>
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    gap: 1,
                }}
            >
                <Avatar src={user?.photo_url} />
                <Typography variant="h5" component="span">
                    {user?.name}
                </Typography>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "row", mt: 1 }}>
                <InfoBox title="Playtime" value="100h 30m" />
                <InfoBox title="Playtime" value="100h 30m" />
            </Box>
        </StyledAnyContentBox>
    );
}

function ProfileDevices() {
    const { data: devices } = useQuery({
        queryFn: getDeviceSessions,
        queryKey: ["DEVICE_SESSIONS"],
        initialData: [],
    });
    return (
        <StyledAnyContentBox>
            <Typography>Registered Devices</Typography>
            <Typography variant="caption">Devices can only be added in Telegram bot</Typography>

            <List>
                {devices?.length === 0 && <Typography>No devices registered</Typography>}
                {devices?.map((val) => (
                    <StyledListItem
                        key={val.created_at}
                        sx={{ alignItems: "center", bgcolor: "background.default", mb: 1, pb: 0 }}
                    >
                        <ListItemText
                            secondary={dateTimeNice(val?.created_at)}
                            primary={"Device"}
                        />
                    </StyledListItem>
                ))}
            </List>
        </StyledAnyContentBox>
    );
}

function RouteComponent() {
    return (
        <>
            <ProfileInfo />
            <GroupList />
            <ProfileDevices />
        </>
    );
}
