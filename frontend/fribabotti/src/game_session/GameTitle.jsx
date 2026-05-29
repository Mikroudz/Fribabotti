import { dateTimeNice, formatSecondsToTime } from "#/utils/helpers";
import { Box, Button, Chip, lighten, Typography } from "@mui/material";
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
                position: "absolute",
                top: 0,
                right: 0,
                m: 0.5,
                bgcolor: isGameOpen ? "secondary.main" : "",
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
                alignItems: "center",
                position: "relative",
                pt: 3,
            }}
        >
            <EndOpenGameSession gameSessionId={data?.id} isGameOpen={!!!data?.ended_at} />
            <Chip
                label={data?.user_group?.name}
                size="small"
                sx={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    m: 0.5,
                    bgcolor: "primary.main",
                }}
            ></Chip>
            <Typography component="span" variant="h4">
                Round
            </Typography>
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
            <Box sx={{ display: "flex", flexDirection: "row", gap: 1 }}>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Par <br /> {data?.user_score?.par}
                </Typography>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Score <br /> {data?.user_score?.total_score}
                </Typography>
            </Box>
            <StackedBarChart scores={data?.user_score?.scores} />
        </StyledAnyContentBox>
    );
}
