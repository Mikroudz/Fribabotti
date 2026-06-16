import { dateTimeNice, formatSecondsToTime } from "#/utils/helpers";
import { Box, Button, Chip, Divider, lighten, Typography } from "@mui/material";
import { StackedBarChart } from "./StackedBar";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { PrettyPar } from "#/components/PrettyPar";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { endGameSession } from "#/utils/api";
import { Link as MuiLink } from "@mui/material";
import { Link } from "@tanstack/react-router";
import { Route as RouteCourse } from "#/routes/course.$courseId.index";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";

function EndOpenGameSession({ gameSessionId, isGameOpen }) {
    const queryClient = useQueryClient();
    const { mutate } = useMutation({
        mutationFn: endGameSession,
        onSuccess: (data) => {
            queryClient.setQueryData(["gamesession", String(data.id)], data);
        },
    });

    return (
        <Button
            size="small"
            sx={{
                m: 0.5,
                bgcolor: isGameOpen ? "secondary.main" : "",
                ml: "auto",
                alignSelf: "flex-end",
            }}
            variant="contained"
            onClick={() => mutate({ data: { close: isGameOpen }, session_id: gameSessionId })}
        >
            {isGameOpen ? "End Game" : "Open Game"}
        </Button>
    );
}

export function GameTitleInformation({ data }) {
    return (
        <StyledAnyContentBox
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "start",
                position: "relative",
                m: 0,
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    alignContent: "center",
                    justifyContent: "space-between",
                    width: "100%",
                }}
            >
                <Typography component="span" variant="h4">
                    Round
                </Typography>
                <Chip
                    label={data?.user_group?.name}
                    size="small"
                    sx={{
                        bgcolor: "primary.main",
                    }}
                ></Chip>
            </Box>

            <MuiLink
                component={Link}
                to={RouteCourse.to}
                params={{ courseId: data?.course_id }}
                from=""
                sx={{ color: "text.primary" }}
            >
                {data?.course?.name} <OpenInNewIcon sx={{ fontSize: "13px" }} />
            </MuiLink>
            <Typography component="span" sx={{ color: "text.secondary", fontSize: "14px" }}>
                {dateTimeNice(data?.started_at)} · {formatSecondsToTime(data?.playtime)}
            </Typography>
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignContent: "center",
                    alignItems: "flex-start",
                    width: "100%",
                }}
            >
                <StyledAnyContentBox
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        pl: 2,
                        pr: 2,
                        pb: 0.5,
                        pt: 0.5,
                        mt: 0,
                        ml: 0,
                        mb: 0,
                        border: 0,
                        bgcolor: (theme) => lighten(theme.palette.background.paper, 0.05),
                    }}
                >
                    <Typography component="span" variant="h6">
                        Total
                    </Typography>

                    <PrettyPar
                        component="span"
                        variant="h5"
                        sx={{ color: "primary.600", fontWeight: 600 }}
                        score={data?.user_score?.total_score}
                        par={data?.user_score?.par}
                    ></PrettyPar>
                </StyledAnyContentBox>
                <Box sx={{ display: "flex", flexDirection: "column", alignSelf: "flex-end" }}>
                    <Typography component="span" sx={{ fontSize: "14px", color: "text.secondary" }}>
                        Par: {data?.user_score?.par}
                    </Typography>
                    <Typography component="span" sx={{ fontSize: "14px", color: "text.secondary" }}>
                        Score: {data?.user_score?.total_score}
                    </Typography>
                </Box>
                <EndOpenGameSession gameSessionId={data?.id} isGameOpen={!!!data?.ended_at} />
            </Box>
            <StackedBarChart scores={data?.user_score?.scores} />
        </StyledAnyContentBox>
    );
}
