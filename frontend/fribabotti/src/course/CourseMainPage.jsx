import { PrettyPar } from "#/components/PrettyPar";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { GameSessionListWithoutName } from "#/game_session/GameSessionList";
import {
    Box,
    Button,
    Dialog,
    DialogContent,
    DialogTitle,
    Divider,
    Grid,
    IconButton,
    Typography,
    useTheme,
} from "@mui/material";

import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { Link, useNavigate } from "@tanstack/react-router";
import { Route as GameSessionRoute } from "#/routes/gamesession_/$gameSessionId/gamesession";
import { Route as RouteEditcourse } from "#/routes/course.$courseId.edit";
import { Route as RouteCourse } from "#/routes/course.$courseId.index";
import { Route as RouteGraph } from "#/routes/course.$courseId.graphs";

import EditIcon from "@mui/icons-material/Edit";
import { Route as RouteNewGame } from "#/routes/course.$courseId.newgame";
import { formatSecondsToTime } from "#/utils/helpers";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import { useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import CloseIcon from "@mui/icons-material/Close";

function SimpleInfoBox({ top, bottom }) {
    return (
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Typography component="span">{top}</Typography>
            <Typography component="span">{bottom}</Typography>
        </Box>
    );
}

function GameTooltip({ active, payload, label }) {
    const firstPayload = payload?.[0];
    const isVisible = active && firstPayload != null;

    return (
        <Box
            sx={{
                visibility: isVisible ? "visible" : "hidden",
                bgcolor: "primary.main",
                p: 1,
                pointerEvents: "auto",
                borderRadius: "6px",
            }}
        >
            {isVisible && (
                <>
                    <Typography>Hole {payload?.[0]?.payload?.track_number}</Typography>
                    <PrettyPar score={payload?.[0]?.payload?.user_avg} wrap={false}></PrettyPar>
                </>
            )}
        </Box>
    );
}

function AverageChart({ data }) {
    const theme = useTheme();

    return (
        <LineChart
            style={{
                width: "350px",
                height: "100%",
                minWidth: "300px",
                minHeight: "400px",
            }}
            responsive
            data={data}
            margin={{
                top: 5,
                right: 0,
                left: 0,
                bottom: 5,
            }}
        >
            <CartesianGrid strokeDasharray="3 3" stroke="#8f8f8f" vertical={false} />
            <XAxis
                dataKey="track_number"
                stroke="white"
                type="category"
                axisLine={false}
                tickLine={false}
                tickMargin={5}
                minTickGap={5}
            />
            <YAxis
                width="auto"
                stroke="white"
                type="number"
                dataKey="user_avg"
                axisLine={false}
                tickLine={false}
            />
            <Legend />
            <Tooltip content={GameTooltip} />

            <Line
                type="monotone"
                dataKey="user_avg"
                stroke={theme.palette.secondary.main}
                name="Average Score"
                strokeWidth={2}
                dot={{
                    fill: theme.palette.secondary.main,
                }}
                activeDot={{ r: 8, stroke: "white" }}
            />
        </LineChart>
    );
}

function SimpleDataDialog({ open, onClose, title, children }) {
    return (
        <Dialog
            open={open}
            onClose={onClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
            maxWidth="md"
            slotProps={{ paper: { sx: { ml: 0.5, mr: 0.5 } } }}
        >
            <DialogTitle id="alert-dialog-title">{title}</DialogTitle>
            <IconButton
                aria-label="close"
                onClick={onClose}
                sx={(theme) => ({
                    position: "absolute",
                    right: 8,
                    top: 8,
                    color: theme.palette.grey[500],
                })}
            >
                <CloseIcon />
            </IconButton>
            <DialogContent sx={{ p: 1 }}>{children}</DialogContent>
        </Dialog>
    );
}

function CourseStatsGlance({ course }) {
    const navigate = useNavigate();
    const handleNavigate = () => {
        navigate({ to: GameSessionRoute.to, params: { gameSessionId: course?.best_round_id } });
    };
    const [openAvgScoreDialog, setOpenAvgScoreDialog] = useState(false);

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
                    <Box onClick={() => setOpenAvgScoreDialog(true)} sx={{ position: "relative" }}>
                        <AnalyticsIcon
                            fontSize="small"
                            sx={{ position: "absolute", right: 0, top: 0, color: "text.secondary" }}
                        ></AnalyticsIcon>
                        <Typography sx={{ color: "text.secondary" }}>Avg Score</Typography>
                        <PrettyPar
                            variant="h4"
                            sx={{ fontWeight: 600 }}
                            score={course?.score_avg}
                            par={course?.total_par}
                            wrap={false}
                            color={"secondary"}
                        ></PrettyPar>
                    </Box>
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
                    <Box
                        onClick={() =>
                            navigate({ to: RouteGraph.to, params: { courseId: course?.id } })
                        }
                        sx={{ position: "relative" }}
                    >
                        <AnalyticsIcon
                            fontSize="small"
                            sx={{ position: "absolute", right: 0, top: 0, color: "text.secondary" }}
                        ></AnalyticsIcon>
                        <Typography sx={{ color: "text.secondary" }}>Games Played</Typography>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                            {course?.games_played_cnt}
                        </Typography>
                    </Box>
                </StyledAnyContentBox>
                <StyledAnyContentBox size={3} component={Grid} sx={{ m: 0, p: 1 }}>
                    <Typography sx={{ color: "text.secondary" }}>Total Playtime</Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        {course?.playtime > 0 ? formatSecondsToTime(course?.playtime) : "-"}
                    </Typography>
                </StyledAnyContentBox>
                <SimpleDataDialog
                    open={openAvgScoreDialog}
                    title="Hole Averages"
                    onClose={() => setOpenAvgScoreDialog(false)}
                >
                    <AverageChart data={course?.tracks} />
                </SimpleDataDialog>
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
