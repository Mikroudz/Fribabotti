import {
    dateTimeNice,
    formatSecondsToTime,
    generateShareableScorecard,
    getScoreEmoji,
} from "#/utils/helpers";
import {
    Box,
    Button,
    Chip,
    Divider,
    IconButton,
    lighten,
    Tooltip,
    Typography,
} from "@mui/material";
import { StackedBarChart } from "./StackedBar";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { PrettyPar } from "#/components/PrettyPar";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { endGameSession } from "#/utils/api";
import { Link as MuiLink } from "@mui/material";
import { Link } from "@tanstack/react-router";
import { Route as RouteCourse } from "#/routes/course.$courseId.index";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import ShareIcon from "@mui/icons-material/Share";
import { SimpleDataDialog } from "#/components/SimpleDialog";
import { useMemo, useState } from "react";
import InfoIcon from "@mui/icons-material/Info";

function EndOpenGameSession({ gameSessionId, isGameOpen }) {
    const queryClient = useQueryClient();
    const { mutate } = useMutation({
        mutationFn: endGameSession,
        onSuccess: (data) => {
            queryClient.setQueryData(["gamesession", parseInt(data.id)], data);
        },
    });

    return (
        <Button
            size="small"
            sx={{
                bgcolor: isGameOpen ? "secondary.main" : "",
            }}
            variant="contained"
            onClick={() => mutate({ data: { close: isGameOpen }, session_id: gameSessionId })}
        >
            {isGameOpen ? "End Game" : "Open Game"}
        </Button>
    );
}

const SCORE_EMOJI_MAP = [
    { text: "No score", score: 0 },
    { text: "Ace", score: 1 },
    { text: "Eagle", score: 2 },
    { text: "Birdie", score: 3 },
    { text: "Par", score: 4 },
    { text: "Bogey", score: 5 },
    { text: "Double bogey", score: 6 },
];

function ShareView({ data, onClose }) {
    const textShareResult = useMemo(() => {
        return generateShareableScorecard(data);
    }, [data]);

    const [copied, setCopied] = useState(false);
    const [infoOpen, setInfoOpen] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(textShareResult);
            setCopied(true);

            // Reset the "Copied!" text after 2 seconds
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error("Failed to copy!", err);
        }
    };

    const handleShare = async () => {
        try {
            if (navigator.share) {
                await navigator.share({
                    title: "Disc Golf",
                    text: textShareResult,
                });
            }
        } catch (err) {
            console.error("Failed to share!", err);
        }
    };

    return (
        <>
            <Typography sx={{ fontSize: "14px", whiteSpace: "pre-line" }}>
                {textShareResult}
            </Typography>

            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignContent: "center",
                    alignItems: "center",
                    gap: 1,
                    justifyContent: "center",
                    mb: 2,
                }}
            >
                <Tooltip
                    describeChild
                    open={infoOpen}
                    onClose={() => setInfoOpen(false)}
                    onOpen={() => setInfoOpen(true)}
                    title={
                        <>
                            {SCORE_EMOJI_MAP.map(
                                (val) => `${val.text} = ${getScoreEmoji(val.score, 4)}\n`,
                            )}
                        </>
                    }
                    placement="bottom"
                    leaveTouchDelay={3000}
                    slotProps={{
                        popper: {
                            sx: {
                                whiteSpace: "pre-line",
                            },
                        },
                    }}
                >
                    <IconButton sx={{ color: "white" }} onClick={() => setInfoOpen(true)}>
                        <InfoIcon />
                    </IconButton>
                </Tooltip>

                <Tooltip
                    describeChild
                    open={copied}
                    onClose={() => setCopied(false)}
                    onOpen={() => setCopied(true)}
                    title="Copied!"
                    placement="top"
                >
                    <Button
                        variant="outlined"
                        sx={{ color: "primary.600", borderColor: "primary.600", width: 110 }}
                        size="small"
                        onClick={handleCopy}
                    >
                        Copy Text
                    </Button>
                </Tooltip>
                <Button
                    variant="contained"
                    size="small"
                    sx={{ color: "primary.800", width: 110 }}
                    onClick={handleShare}
                >
                    Share Text
                </Button>
                <Button
                    variant="outlined"
                    size="small"
                    sx={{ color: "grey", borderColor: "#80808057" }}
                    onClick={onClose}
                >
                    Close
                </Button>
            </Box>
        </>
    );
}

function ShareGame({ data }) {
    const [dialogOpen, setOpenDialog] = useState(false);

    return (
        <>
            <Button
                size="small"
                sx={{
                    position: "absolute", // go outside parent box to overlap previous line, bit hacky but works
                    top: -40,
                    right: 0,
                }}
                endIcon={<ShareIcon />}
                variant="outlined"
                color="secondary"
                onClick={() => setOpenDialog(true)}
            >
                Share
            </Button>
            <SimpleDataDialog
                open={dialogOpen}
                title="Share Game"
                onClose={() => setOpenDialog(false)}
            >
                <ShareView data={data} onClose={() => setOpenDialog(false)} />
            </SimpleDataDialog>
        </>
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
                <Box
                    sx={{
                        m: 0.5,
                        ml: "auto",
                        alignSelf: "flex-end",
                        display: "flex",
                        flexDirection: "column",
                        position: "relative",
                    }}
                >
                    <ShareGame data={data} />
                    <EndOpenGameSession gameSessionId={data?.id} isGameOpen={!!!data?.ended_at} />
                </Box>
            </Box>
            <StackedBarChart scores={data?.user_score?.scores} />
        </StyledAnyContentBox>
    );
}
