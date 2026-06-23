import { StyledListItem, StyledListItemButton } from "#/components/List";
import { useUserGroup } from "#/hooks/ProfileHooks";
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Avatar,
    AvatarGroup,
    Box,
    Button,
    IconButton,
    List,
    ListItemAvatar,
    ListItemIcon,
    ListItemSecondaryAction,
    ListItemText,
    Menu,
    MenuItem,
    Stack,
    Typography,
} from "@mui/material";
import {
    createFileRoute,
    Link,
    useLocation,
    useNavigate,
    useParams,
    useRouter,
} from "@tanstack/react-router";
import { Route as GameRoute } from "../gamesession_/$gameSessionId/gamesession";
import { Route as InviteRoute } from "./join.$inviteCode";
import { Route as EditGroupRoute } from "./$groupId.edit";
import { Route as AddUserRoute } from "./$groupId.add_member";

import { dateTimeNice } from "#/utils/helpers";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { ClickToCopy } from "#/components/ClickToCopy";
import { useState } from "react";
import { AppBarAction } from "#/context/AppBarPortal";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import DeleteConfirmation from "#/components/SimpleDialog";
import { createGroup } from "#/utils/api";
import { useMutation } from "@tanstack/react-query";

export const Route = createFileRoute("/groups/$groupId/")({
    component: RouteComponent,
    beforeLoad: () => ({
        headerTitle: "Group",
    }),
});

function AppBarMenu({ group_id }) {
    const [anchorEl, setAnchorEl] = useState(null);
    const navigate = useNavigate();
    const { mutate } = useMutation({
        mutationFn: createGroup,
    });
    const [openDeleteGroupDialog, setOpenDeleteGroupDialog] = useState(false);

    const handleDeleteGroup = () => {
        mutate(
            { method: "DELETE", data: { id: group_id } },
            {
                onSuccess: () => {
                    // go to home after deletion
                    // TODO: add snackbar confirmation
                    navigate({ to: "/" });
                },
                onError: (e) => {
                    console.warn("Deletion failed in backend", e);
                },
            },
        );
    };

    return (
        <AppBarAction>
            <IconButton size="large" onClick={(e) => setAnchorEl(e.currentTarget)}>
                <MoreVertIcon sx={{ color: "text.primary" }} />
            </IconButton>
            <Menu open={!!anchorEl} onClose={() => setAnchorEl(null)} anchorEl={anchorEl}>
                <MenuItem onClick={() => navigate({ to: EditGroupRoute.to, params: { groupId: group_id } })}>
                    <ListItemIcon sx={{ color: "text.primary" }}>
                        <EditIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Edit Group</ListItemText>
                </MenuItem>
                <MenuItem onClick={() => setOpenDeleteGroupDialog(true)}>
                    <ListItemIcon sx={{ color: "text.primary" }}>
                        <DeleteIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Delete Group</ListItemText>
                </MenuItem>
            </Menu>
            <DeleteConfirmation
                open={openDeleteGroupDialog}
                onClose={() => setOpenDeleteGroupDialog(false)}
                title={"Delete Group"}
                contentText={"Do you want to delete this Group permanently?"}
                onDelete={handleDeleteGroup}
            />
        </AppBarAction>
    );
}

function GroupInfo() {
    const params = useParams({ strict: false });
    const { groupId } = params;
    const location = useLocation();
    const router = useRouter();

    const { data: group } = useUserGroup(groupId);
    const inviteLink = router.buildLocation({
        to: InviteRoute.to,
        params: { inviteCode: group?.invite_code },
    });

    const basepath = router.options.basepath || "/";

    const origin = typeof window !== "undefined" ? window.location.origin : "";
    const appRootUrl = `${origin}${basepath.replace(import.meta.env.VITE_BASE_PATH, "").replace(new RegExp("/$"), "")}`;

    const memberAvatars = group?.members?.reduce((acc, m) => {
        acc[m.id] = m.photo_url;
        return acc;
    }, {});

    return (
        <Stack sx={{ m: 1 }}>
            <AppBarMenu group_id={groupId} />
            <StyledAnyContentBox sx={{ p: 1, m: 0, mb: 1 }}>
                <Typography variant="h6">{group?.name}</Typography>
                <Accordion sx={{ bgcolor: "primary.main", m: 0 }} disableGutters>
                    <AccordionSummary
                        expandIcon={<ArrowDropDownIcon />}
                        sx={{
                            minHeight: 32,
                            height: 32,
                        }}
                    >
                        <Typography component="span">Get Invite Link</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Typography component="span">{`${appRootUrl}${inviteLink.href}`}</Typography>
                        <ClickToCopy textToCopy={`${appRootUrl}${inviteLink.href}`} />
                    </AccordionDetails>
                </Accordion>
            </StyledAnyContentBox>

            <Box
                sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignContent: "center",
                    alignItems: "center",
                    width: "100%",
                }}
            >
                <Typography>Group Members {group?.members?.length}</Typography>
                <Button
                    component={Link}
                    variant="outlined"
                    sx={{
                        borderColor: "primary.600",
                        color: "primary.600",
                        ml: "auto",
                    }}
                    to={AddUserRoute.to}
                    params={{ groupId: group?.id }}
                >
                    + Add Member
                </Button>
            </Box>
            <List>
                {group?.members?.map((user) => (
                    <StyledListItem sx={{ p: 1 }} key={user.id}>
                        <ListItemAvatar>
                            <Avatar src={user.photo_url} />
                        </ListItemAvatar>
                        <ListItemText primary={user.name}></ListItemText>
                    </StyledListItem>
                ))}
            </List>
            <Typography>Recent Games</Typography>

            <List>
                {group?.recent_games?.map((game) => (
                    <StyledListItem sx={{ p: 0 }} key={game.id}>
                        <StyledListItemButton
                            component={Link}
                            to={GameRoute.to}
                            params={{ gameSessionId: game.id }}
                            from={location.pathname}
                        >
                            <ListItemText
                                primary={game.course_name}
                                secondary={dateTimeNice(game.started_at)}
                            />
                        </StyledListItemButton>
                        <ListItemSecondaryAction>
                            <AvatarGroup
                                max={4}
                                sx={{
                                    "& .MuiAvatar-root": { width: 24, height: 24, fontSize: 12 },
                                }}
                            >
                                {game.participants?.map((p) => (
                                    <Avatar src={memberAvatars[p]} sizes="small" />
                                ))}
                            </AvatarGroup>
                        </ListItemSecondaryAction>
                    </StyledListItem>
                ))}
            </List>
        </Stack>
    );
}

function RouteComponent() {
    return <GroupInfo />;
}
