import { PrettyPar, prettyParFormat } from "#/components/PrettyPar";
import { Box, Typography } from "@mui/material";
import { Fragment } from "react/jsx-runtime";

const chunkArray = (arr, size) => {
    if (!Array.isArray(arr)) {
        return [];
    }
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
        chunks.push(arr.slice(i, i + size));
    }
    return chunks;
};

export function ScoreCard({ data }) {
    const chunked = chunkArray(data?.user_score.scores, 8);
    // Todo: handle scores from many users
    const user_scores = data?.user_score ? [data?.user_score] : [];
    const trackTotalPar = data?.user_score?.par ?? 0;

    return (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5, ml: 0.5, mr: 0.5 }}>
            {chunked.map((chunk, chunkIndex) => (
                <Fragment key={chunkIndex}>
                    <Box
                        sx={{
                            display: "grid",
                            gridTemplateColumns: "2fr repeat(8, minmax(0, 1fr))",
                            gap: 0.5,
                        }}
                    >
                        <Box
                            sx={{
                                gridColumn: "1 / -1",
                                display: "grid",
                                gridTemplateColumns: "subgrid",
                                borderBottom: "1px solid",
                                borderBottomColor: "divider",
                                mt: chunkIndex > 0 ? 2 : 0,
                            }}
                        >
                            <Box
                                sx={{
                                    display: "flex",
                                    flexDirection: "column",
                                    fontWeight: "bold",
                                    alignItems: "center",
                                }}
                            >
                                <Typography
                                    component="span"
                                    sx={{ color: "text.secondary", fontSize: "13px", flexGrow: 1 }}
                                >
                                    HOLE
                                </Typography>
                                <Typography
                                    component="span"
                                    sx={{ color: "text.secondary", fontSize: "13px", flexGrow: 1 }}
                                >
                                    DIST
                                </Typography>
                                <Typography
                                    component="span"
                                    sx={{ color: "text.secondary", fontSize: "13px", flexGrow: 1 }}
                                >
                                    PAR
                                </Typography>
                            </Box>

                            {chunk.map((val) => (
                                <Box
                                    key={val.track_number}
                                    sx={{
                                        display: "flex",
                                        flexDirection: "column",
                                        alignItems: "center",
                                    }}
                                >
                                    <Typography component="span" sx={{ fontWeight: "bold" }}>
                                        {val.track_number}
                                    </Typography>
                                    <Typography component="span" sx={{ fontSize: "13px" }}>
                                        0
                                    </Typography>
                                    <Typography component="span" sx={{ fontWeight: "bold" }}>
                                        {val.par}
                                    </Typography>
                                </Box>
                            ))}
                            <Box
                                sx={{
                                    display: "flex",
                                    flexDirection: "column",
                                    fontWeight: "bold",
                                    alignItems: "center",
                                }}
                            >
                                <Typography component="span" sx={{ fontSize: "13px", flexGrow: 1 }}>
                                    total
                                </Typography>
                                <Typography
                                    component="span"
                                    sx={{ color: "text.secondary", fontSize: "13px", flexGrow: 1 }}
                                >
                                    0
                                </Typography>
                                <Typography
                                    component="span"
                                    sx={{ color: "text.secondary", fontSize: "13px", flexGrow: 1 }}
                                >
                                    {trackTotalPar}
                                </Typography>
                            </Box>
                        </Box>
                        {user_scores.map((user) => (
                            <Box
                                key={user.username}
                                sx={{
                                    gridColumn: "1 / -1",
                                    display: "grid",
                                    gridTemplateColumns: "subgrid",
                                    alignItems: "center",
                                }}
                            >
                                <Typography
                                    sx={{
                                        fontSize: "14px",
                                        fontWeight: "bold",
                                        textAlign: "center",
                                    }}
                                >
                                    {user.username}
                                </Typography>

                                {chunk.map((val) => {
                                    const scoreData = user.scores.find(
                                        (s) => s.track_number === val.track_number,
                                    );

                                    return (
                                        <Box
                                            key={`score-${val.track_number}`}
                                            sx={{ display: "flex", justifyContent: "center" }}
                                        >
                                            <PrettyPar
                                                sx={{ fontWeight: "bold" }}
                                                score={scoreData?.score}
                                                par={val.par}
                                                coloredContainer={true}
                                            ></PrettyPar>
                                        </Box>
                                    );
                                })}
                                <Box
                                    sx={{
                                        display: "flex",
                                        flexDirection: "column",
                                        alignItems: "center",
                                    }}
                                >
                                    <PrettyPar
                                        wrap={false}
                                        score={user.total_score}
                                        par={user.par}
                                        sx={{ lineHeight: "1em" }}
                                    />
                                    <Typography
                                        component="span"
                                        sx={{ fontSize: "14px", lineHeight: "1em" }}
                                    >
                                        ({user.total_score})
                                    </Typography>
                                </Box>
                            </Box>
                        ))}
                    </Box>
                </Fragment>
            ))}
        </Box>
    );
}
