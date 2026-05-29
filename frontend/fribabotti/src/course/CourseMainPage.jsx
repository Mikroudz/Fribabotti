import { PrettyPar } from "#/components/PrettyPar";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { GameSessionListWithoutName } from "#/game_session/GameSessionList";
import { Box, Button, Divider, Grid, IconButton, Typography } from "@mui/material";

import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { Link, useNavigate } from "@tanstack/react-router";
import { Route as GameSessionRoute } from "#/routes/gamesession_/$gameSessionId/gamesession";
import { Route as RouteEditcourse } from "#/routes/course.$courseId.edit";
import { Route as RouteCourse } from "#/routes/course.$courseId.index";

import EditIcon from "@mui/icons-material/Edit";
import { Route as RouteNewGame } from "#/routes/course.$courseId.newgame";
import { formatSecondsToTime } from "#/utils/helpers";

function SimpleInfoBox({ top, bottom }) {
    return (
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Typography component="span">{top}</Typography>
            <Typography component="span">{bottom}</Typography>
        </Box>
    );
}

function CourseStatsGlance({ course }) {
    const navigate = useNavigate();
    const handleNavigate = () => {
        navigate({ to: GameSessionRoute.to, params: { gameSessionId: course?.best_round_id } });
    };

    return (
        <>
            <StyledAnyContentBox sx={{ display: "flex", flexDirection: "column" }}>
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "row",
                        width: "100%",
                        justifyContent: "space-between",
                    }}
                >
                    <Typography component="span" variant="h5">
                        {course?.name}
                    </Typography>
                    <IconButton
                        sx={{ pt: 0, pr: 0 }}
                        onClick={async () =>
                            await navigate({
                                to: RouteEditcourse.to,
                                params: { courseId: course?.id },
                                from: RouteCourse.fullPath,
                            })
                        }
                    >
                        <EditIcon sx={{ color: "white" }} />
                    </IconButton>
                </Box>

                <Divider />
                <Box sx={{ display: "flex", flexDirection: "row", gap: 2, mb: 2 }}>
                    <SimpleInfoBox top="Holes" bottom={course?.tracks?.length} />
                    <SimpleInfoBox
                        top="Par"
                        bottom={course?.tracks?.reduce((acc, val) => acc + val.par, 0)}
                    />
                    <SimpleInfoBox top="Distance" bottom="2500m" />
                </Box>
                <Button
                    nativeButton={false}
                    variant="contained"
                    sx={{ bgcolor: "secondary.main", width: "100%" }}
                    component={Link}
                    to={RouteNewGame.to}
                    params={course?.id}
                >
                    Start new round
                </Button>
            </StyledAnyContentBox>
            <Typography sx={{ pl: 1 }} component="span">
                Course Statistics
            </Typography>
            <Grid container spacing={1} sx={{ m: 1 }} columns={{ xs: 6, sm: 12 }}>
                <StyledAnyContentBox component={Grid} size={3} sx={{ m: 0, p: 1 }}>
                    <Typography sx={{ color: "text.secondary" }}>Avg Score</Typography>
                    <PrettyPar
                        variant="h4"
                        sx={{ fontWeight: 600 }}
                        score={course?.score_avg}
                        par={course?.total_par}
                        wrap={false}
                        color={"secondary"}
                    ></PrettyPar>
                </StyledAnyContentBox>
                <StyledAnyContentBox component={Grid} size={3} sx={{ m: 0, p: 1 }}>
                    <Box onClick={handleNavigate} sx={{ position: "relative" }}>
                        <OpenInNewIcon
                            fontSize="small"
                            sx={{ position: "absolute", right: 0, top: 0, color: "text.secondary" }}
                        ></OpenInNewIcon>
                        <Typography sx={{ color: "text.secondary" }}>Best Round</Typography>

                        <PrettyPar
                            variant="h4"
                            sx={{ fontWeight: 600 }}
                            score={course?.best_round}
                            par={course?.total_par}
                            wrap={false}
                            color={"secondary"}
                        ></PrettyPar>
                    </Box>
                </StyledAnyContentBox>

                <StyledAnyContentBox component={Grid} size={3} sx={{ m: 0, p: 1 }}>
                    <Typography sx={{ color: "text.secondary" }}>Hypothetical Best</Typography>

                    <PrettyPar
                        variant="h4"
                        sx={{ fontWeight: 600 }}
                        score={course?.hypothetical_best}
                        par={course?.total_par}
                        wrap={false}
                        color={"secondary"}
                    ></PrettyPar>
                </StyledAnyContentBox>
                <StyledAnyContentBox size={{ xs: 3, sm: 3 }} component={Grid} sx={{ m: 0, p: 1 }}>
                    <Typography sx={{ color: "text.secondary" }}>Games Played</Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        {course?.games_played_cnt}
                    </Typography>
                </StyledAnyContentBox>
                <StyledAnyContentBox size={3} component={Grid} sx={{ m: 0, p: 1 }}>
                    <Typography sx={{ color: "text.secondary" }}>Total Playtime</Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        {course?.playtime > 0 ? formatSecondsToTime(course?.playtime) : "-"}
                    </Typography>
                </StyledAnyContentBox>
            </Grid>
        </>
    );
}

export function CourseMainPage({ course }) {
    return (
        <>
            <CourseStatsGlance course={course} />
            <Typography sx={{ pl: 1 }} component="span">
                Recent Round
            </Typography>
            <GameSessionListWithoutName
                gameSessions={course?.user_recent_rounds}
                course_par={course?.total_par}
            />
        </>
    );
}
