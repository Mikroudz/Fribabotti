import { GameTitleInformation } from "#/game_session/GameTitle";
import { ScoreCard } from "#/game_session/Scorecard";
import { Box, Button, IconButton, ListItemIcon, ListItemText, Menu, MenuItem } from "@mui/material";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Route as MapRoute } from "./_sessionlayout.map";
import { useGameSession } from "#/hooks/GameSessionHooks";
import { AppBarAction } from "#/context/AppBarPortal";
import { useState } from "react";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import DeleteIcon from "@mui/icons-material/Delete";
import { useMutation } from "@tanstack/react-query";
import { createGameSession } from "#/utils/api";
import DeleteConfirmation from "#/components/SimpleDialog";

export const Route = createFileRoute("/gamesession_/$gameSessionId/gamesession")({
    component: RouteComponent,
});

function AppBarMenu({ data }) {
    const [anchorEl, setAnchorEl] = useState(null);
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
            </Menu>
            <DeleteConfirmation
                open={openDeleteGameDialog}
                onClose={() => setOpenDeleteGameDialog(false)}
                title={"Delete Gamesession"}
                contentText={"Do you want to delete this gamesession permanently?"}
                onDelete={handleDeleteGame}
            />
        </AppBarAction>
    );
}

function RouteComponent() {
    const { gameSessionId } = Route.useParams();
    const { data, status } = useGameSession(gameSessionId);

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

            <ScoreCard data={data} />

            <AppBarMenu data={data} />
        </Box>
    );
}
