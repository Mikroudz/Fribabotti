import { dateTimeNice } from "#/utils/helpers";
import { Box, Typography, useTheme } from "@mui/material";
import { StackedBarChart } from "./StackedBar";

export function GameTitleInformation({ data }) {
    const userScoreTotal = data?.user_score?.total_score - data?.user_score?.par;

    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                m: 1,
                p: 1,
                alignItems: "center",
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                borderRadius: "7px",
            }}
        >
            <Typography component="span" variant="h4">
                Round
            </Typography>
            <Typography component="span">{data?.course?.name}</Typography>
            <Typography component="span" sx={{ color: "text.secondary", fontSize: "14px" }}>
                {dateTimeNice(data?.started_at)}
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <Typography component="span" variant="h6">
                    Total
                </Typography>

                <Typography component="span" variant="h6">
                    {!userScoreTotal ? 0 : userScoreTotal}
                </Typography>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "row", gap: 1 }}>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Par <br /> {data?.user_score?.par}
                </Typography>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Score <br /> {data?.user_score?.total_score}
                </Typography>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Birdie <br />5
                </Typography>
            </Box>
            <StackedBarChart scores={data?.user_score?.scores} />
        </Box>
    );
}
