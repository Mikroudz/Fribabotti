import { dateTimeNice } from "#/utils/helpers";
import { Box, lighten, Typography } from "@mui/material";
import { StackedBarChart } from "./StackedBar";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";

export function GameTitleInformation({ data }) {
    const userScoreTotal = data?.user_score?.total_score - data?.user_score?.par;

    return (
        <StyledAnyContentBox
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
            }}
        >
            <Typography component="span" variant="h4">
                Round
            </Typography>
            <Typography component="span">{data?.course?.name}</Typography>
            <Typography component="span" sx={{ color: "text.secondary", fontSize: "14px" }}>
                {dateTimeNice(data?.started_at)}
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

                <Typography
                    component="span"
                    variant="h5"
                    sx={{ color: "primary.600", fontWeight: 600 }}
                >
                    {!userScoreTotal ? 0 : userScoreTotal}
                </Typography>
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
