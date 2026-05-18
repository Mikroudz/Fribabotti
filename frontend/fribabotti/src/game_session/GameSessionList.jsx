import { Box, List, ListItemText, Typography } from "@mui/material";
import { useGameSessions } from "../hooks/GameSessionHooks";
import { dateTimeNice } from "../utils/helpers";
import { StyledListItem, StyledListItemButton } from "#/components/List";
import { PrettyPar } from "#/components/PrettyPar";
import { Link } from "@tanstack/react-router";
import { Route as GameSessionRoute } from "#/routes/gamesession_/$gameSessionId/gamesession";

export function GameSessionList() {
    const { data: gameSessions, status } = useGameSessions();
    return (
        <List dense sx={{ m: 1 }}>
            {gameSessions?.map((val) => (
                <StyledListItem
                    key={val.id}
                    secondaryAction={
                        <Box sx={{ display: "flex", flexDirection: "column" }}>
                            <PrettyPar score={5} par={4} />
                            <Typography
                                component="span"
                                variant="caption"
                                sx={{ color: "text.secondary" }}
                            >
                                vs par
                            </Typography>
                        </Box>
                    }
                    sx={{ alignItems: "center" }}
                >
                    <StyledListItemButton
                        component={Link}
                        to={GameSessionRoute.to}
                        params={{ gameSessionId: val.id }}
                    >
                        <ListItemText
                            primary={val?.course?.name}
                            secondary={dateTimeNice(val?.started_at)}
                        />
                    </StyledListItemButton>
                </StyledListItem>
            ))}
        </List>
    );
}
