import { useUser } from "#/auth/UserHooks";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { GroupList } from "#/Groups/GroupList";
import { Avatar, Box, lighten, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/profile/")({
    component: RouteComponent,
    beforeLoad: () => ({
        headerTitle: "Profile",
    }),
});

function InfoBox({ title, value }) {
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
    console.log(user);
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

function RouteComponent() {
    return (
        <>
            <ProfileInfo />
            <GroupList />
        </>
    );
}
