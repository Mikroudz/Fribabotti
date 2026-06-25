import { GameTitleInformation } from "#/game_session/GameTitle";
import { ScoreCard } from "#/game_session/Scorecard";
import {
    Avatar,
    Box,
    Button,
    IconButton,
    List,
    ListItemAvatar,
    ListItemButton,
    ListItemIcon,
    ListItemSecondaryAction,
    ListItemText,
    Menu,
    MenuItem,
} from "@mui/material";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Route as MapRoute } from "./_sessionlayout.map";
import { useGameSession } from "#/hooks/GameSessionHooks";
import { AppBarAction } from "#/context/AppBarPortal";
import { useState } from "react";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import DeleteIcon from "@mui/icons-material/Delete";
import { useMutation } from "@tanstack/react-query";
import { addUsersGamesession, createGameSession } from "#/utils/api";
import DeleteConfirmation, { SimpleDataDialog } from "#/components/SimpleDialog";
import GroupAddIcon from "@mui/icons-material/GroupAdd";
import { useUserGroup } from "#/hooks/ProfileHooks";
import ListSkeletonLoader from "#/components/Loaders";
import { StyledListItem } from "#/components/List";
import { CheckBox } from "@mui/icons-material";
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";

export const Route = createFileRoute("/gamesession_/$gameSessionId/gamesession")({
    component: RouteComponent,
});

function AddPlayersList({ data }) {
    const { data: group, isPending } = useUserGroup(data?.user_group_id);
    const [checkedIds, setCheckedIds] = useState([]);
    const { mutate } = useMutation({ mutationFn: addUsersGamesession, onSuccess: () => {} });

    if (isPending) return <ListSkeletonLoader />;
    const others = data?.other_scores?.map((val) => val.user_id) || [];
    const users_in_game = [data?.user_score?.user_id, ...others];
    const handleChecked = (id) => {
        if (checkedIds.findIndex((val) => val === id) === -1) {
            setCheckedIds((prev) => [...prev, id]);
        } else {
            setCheckedIds((prev) => prev.filter((val) => val !== id));
        }
    };

    // TODO: users can be removed from game
    return (
        <>
            <Button onClick={() => mutate({ data: checkedIds, game_id: data.id })} variant="contained">
                Save
            </Button>
            <List sx={{ width: "350px" }}>
                {group?.members
                    ?.filter((u) => !users_in_game.includes(u.id))
                    .map((user) => (
                        <StyledListItem sx={{ p: 0 }} key={user.id}>
                            <ListItemButton sx={{ m: 0, p: 1 }} onClick={() => handleChecked(user.id)}>
                                <ListItemAvatar>
                                    <Avatar src={user.photo_url} />
                                </ListItemAvatar>
                                <ListItemText primary={user.name}></ListItemText>
                                <ListItemSecondaryAction>
                                    {checkedIds.includes(user.id) ? (
                                        <CheckBox />
                                    ) : (
                                        <CheckBoxOutlineBlankIcon />
                                    )}
                                </ListItemSecondaryAction>
                            </ListItemButton>
                        </StyledListItem>
                    ))}
            </List>
        </>
    );
}

function AppBarMenu({ data }) {
    const [anchorEl, setAnchorEl] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const navigate = useNavigate();
    const [openDeleteGameDialog, setOpenDeleteGameDialog] = useState(false);
    const { mutate } = useMutation({
        mutationFn: createGameSession,
    });

    const handleDeleteGame = () => {
        mutate(
            { method: "DELETE", data: { id: data?.id } },
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
                <MenuItem onClick={() => setOpenDeleteGameDialog(true)}>
                    <ListItemIcon sx={{ color: "text.primary" }}>
                        <DeleteIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Delete Session</ListItemText>
                </MenuItem>
                <MenuItem onClick={() => setOpenDialog(true)}>
                    <ListItemIcon sx={{ color: "text.primary" }}>
                        <GroupAddIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Add Players</ListItemText>
                </MenuItem>
            </Menu>
            <DeleteConfirmation
                open={openDeleteGameDialog}
                onClose={() => setOpenDeleteGameDialog(false)}
                title={"Delete Gamesession"}
                contentText={"Do you want to delete this gamesession permanently?"}
                onDelete={handleDeleteGame}
            />
            <SimpleDataDialog open={openDialog} title="Add Players" onClose={() => setOpenDialog(false)}>
                <AddPlayersList data={data} />
            </SimpleDataDialog>
        </AppBarAction>
    );
}

function RouteComponent() {
    const { gameSessionId } = Route.useParams();
    const { data, status } = useGameSession();

    const scores = data && [data?.user_score, ...data?.other_scores];

    return (
        <Box sx={{ p: 1 }}>
            <GameTitleInformation data={data} />
            <Button
                variant="contained"
                sx={{ bgcolor: "secondary.main", width: "100%", mb: 1, mt: 1 }}
                component={Link}
                to={MapRoute.to}
                params={{ gameSessionId }}
            >
                Map/Play
            </Button>

            <ScoreCard data={scores} />

            <AppBarMenu data={data} />
        </Box>
    );
}
