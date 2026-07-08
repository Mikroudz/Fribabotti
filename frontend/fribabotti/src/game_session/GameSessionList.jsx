import { Box, List, ListItemText, Typography } from "@mui/material";
import { dateTimeNice } from "../utils/helpers";
import { StyledListItem, StyledListItemButton } from "#/components/List";
import { PrettyPar, prettyParFormat } from "#/components/PrettyPar";
import { Link } from "@tanstack/react-router";
import { Route as GameSessionRoute } from "#/routes/gamesession_/$gameSessionId/gamesession";
import AcUnitIcon from "@mui/icons-material/AcUnit";
export function GameSessionList({ gameSessions }) {
    return (
        <List dense>
            {gameSessions?.map((val) => (
                <StyledListItem
                    key={val.id}
                    secondaryAction={
                        <Box sx={{ display: "flex", flexDirection: "column" }}>
                            <PrettyPar score={val.user_score} par={val.par} />
                            <Typography component="span" variant="caption" sx={{ color: "text.secondary" }}>
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
                        from=""
                        sx={{ display: "flex", flexDirection: "column", alignItems: "start" }}
                    >
                        <Box sx={{ display: "flex", flexDirection: "row", gap: 1, alignItems: "flex-start" }}>
                            <Typography
                                component="span"
                                sx={{
                                    display: "flex",
                                    width: "36px",
                                    justifyContent: "center",
                                    textAlign: "center",
                                    alignItems: "center",
                                    bgcolor: "primary.300",
                                    aspectRatio: "1/1",
                                    borderRadius: "7px",
                                    p: 1,
                                    mt: 1,
                                }}
                            >
                                <AcUnitIcon />
                            </Typography>
                            <Box sx={{ display: "flex", flexDirection: "column" }}>
                                <Typography component="span" variant="h6">
                                    {val?.course?.name}
                                </Typography>
                                <Typography
                                    component="span"
                                    variant="caption"
                                    sx={{ color: "text.secondary" }}
                                >
                                    {dateTimeNice(val?.started_at)} · {val?.course?.holes}
                                </Typography>
                            </Box>
                        </Box>
                    </StyledListItemButton>
                </StyledListItem>
            ))}
        </List>
    );
}

export function GameSessionListWithoutName({ gameSessions, course_par = 0 }) {
    return (
        <List dense sx={{ m: 1, mt: 0 }}>
            {gameSessions?.map((val) => (
                <StyledListItem key={val.id} sx={{ alignItems: "center" }}>
                    <StyledListItemButton
                        component={Link}
                        to={GameSessionRoute.to}
                        params={{ gameSessionId: val.id }}
                    >
                        <ListItemText
                            secondary={`${prettyParFormat(val.score, course_par)} vsPar`}
                            primary={dateTimeNice(val?.started_at)}
                        />
                    </StyledListItemButton>
                </StyledListItem>
            ))}
        </List>
    );
}
