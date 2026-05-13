import { PrettyPar } from "#/components/PrettyPar";
import { Box, Divider, Typography } from "@mui/material";

const chunkArray = (arr, size) => {
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
        chunks.push(arr.slice(i, i + size));
    }
    return chunks;
};

export function ScoreCard() {
    const data = [
        { track_number: 1, par: 3, throws: [1, 3, 5] },
        { track_number: 2, par: 3, throws: [1, 3, 5] },
        { track_number: 3, par: 3, throws: [1, 3, 5] },
        { track_number: 4, par: 3, throws: [1, 3, 5] },
        { track_number: 5, par: 3, throws: [1, 3, 5] },
        { track_number: 6, par: 3, throws: [1, 3, 5] },
        { track_number: 7, par: 3, throws: [1, 3, 5] },
        { track_number: 8, par: 3, throws: [1, 3, 5] },
        { track_number: 9, par: 3, throws: [1, 3, 5] },
        { track_number: 10, par: 3, throws: [1, 3, 5] },
        { track_number: 11, par: 3, throws: [1, 3, 5] },
    ];
    const userScore = [
        {
            user: "mikroudz",
            scores: [
                { track_number: 1, throws: [1, 3, 5] },
                { track_number: 2, throws: [1, 3, 5] },
                { track_number: 3, throws: [1, 3, 5] },
                { track_number: 4, throws: [1, 3, 5] },
                { track_number: 5, throws: [1, 3, 5] },
                { track_number: 6, throws: [1, 3, 5] },
                { track_number: 7, throws: [1, 3, 5] },
                { track_number: 8, throws: [1, 3, 5] },
                { track_number: 9, throws: [1, 3, 5] },
                { track_number: 10, throws: [1, 3, 5] },
                { track_number: 11, throws: [1, 3, 5] },
            ],
        },
    ];

    const chunked = chunkArray(data, 8);

    return (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
            {chunked.map((chunk, chunkIndex) => (
                <>
                    <Box
                        key={chunkIndex}
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
                        </Box>
                        {userScore.map((user) => (
                            <Box
                                key={user.user}
                                sx={{
                                    gridColumn: "1 / -1",
                                    display: "grid",
                                    gridTemplateColumns: "subgrid",
                                    alignItems: "center",
                                }}
                            >
                                <Typography sx={{ fontSize: "14px", fontWeight: "bold" }}>
                                    {user.user}
                                </Typography>

                                {chunk.map((val) => {
                                    const scoreData = user.scores.find(
                                        (s) => s.track_number === val.track_number,
                                    );
                                    const throwsCount = scoreData ? scoreData.throws.length : "-";

                                    return (
                                        <Box
                                            key={`score-${val.track_number}`}
                                            sx={{ display: "flex", justifyContent: "center" }}
                                        >
                                            <PrettyPar
                                                sx={{ fontWeight: "bold" }}
                                                score={throwsCount}
                                                par={val.par}
                                            ></PrettyPar>
                                        </Box>
                                    );
                                })}
                            </Box>
                        ))}
                    </Box>
                </>
            ))}
        </Box>
    );
}
