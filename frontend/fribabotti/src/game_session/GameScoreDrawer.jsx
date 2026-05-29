import { Box, Chip, IconButton, SwipeableDrawer, Typography } from "@mui/material";
import { useState } from "react";
import { calcTotalFromScores, PlayersHoleScores } from "./PlayersScores";
import { useGameSession, useHoleChanger, useSelectedHole } from "#/hooks/GameSessionHooks";
import { prettyParFormat } from "#/components/PrettyPar";
import { useGameState } from "#/context/GameSessionData";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { ChevronLeft, ChevronRight } from "@mui/icons-material";

export function GameScoreDrawer() {
    const { data: gameSessionData } = useGameSession();
    const selectedHole = useSelectedHole();
    const currentHoleScore = useGameState();
    const { moveToNextHole, moveToPreviousHole } = useHoleChanger();

    const [isOpen, setIsOpen] = useState(false);

    const toggleDrawer = (openState) => (event) => {
        // Prevent interaction issues with keyboard navigation
        if (event && event.type === "keydown" && (event.key === "Tab" || event.key === "Shift")) {
            return;
        }
        setIsOpen(openState);
    };

    const NAV_HEIGHT = 56;
    const VISIBLE_HANDLE = 40;
    const TOTAL_BLEED = NAV_HEIGHT + VISIBLE_HANDLE;
    const [total_score, total_par] = calcTotalFromScores(gameSessionData?.user_score?.scores);

    return (
        <SwipeableDrawer
            anchor="bottom"
            swipeAreaWidth={TOTAL_BLEED}
            disableDiscovery={true}
            open={isOpen}
            onClose={toggleDrawer(false)}
            onOpen={toggleDrawer(true)}
            slotProps={{
                paper: {
                    sx: {
                        height: "50%",
                        overflow: "visible",
                    },
                },
                swipeArea: {
                    sx: {
                        height: `${VISIBLE_HANDLE}px !important`,
                        bottom: `${NAV_HEIGHT}px !important`,
                    },
                },
            }}
            ModalProps={{
                keepMounted: true,
            }}
        >
            <Box
                onClick={toggleDrawer(!isOpen)}
                sx={{
                    position: "absolute",
                    top: -TOTAL_BLEED,
                    left: 0,
                    right: 0,
                    height: TOTAL_BLEED,
                    visibility: "visible",
                    display: "flex",
                    justifyContent: "center",
                    bgcolor: "primary.300",
                    borderTopLeftRadius: 16,
                    borderTopRightRadius: 16,
                    cursor: "pointer",
                }}
            >
                <Box sx={{ position: "absolute", left: 0, m: 0.5, display: "flex", gap: 1 }}>
                    <Chip
                        label={`Total ${prettyParFormat(total_score, total_par)}`}
                        sx={{ bgcolor: "primary.500" }}
                    ></Chip>
                    <Chip
                        label={`Hole ${selectedHole?.track_number}`}
                        sx={{ bgcolor: "primary.500" }}
                    ></Chip>
                </Box>
                <Box sx={{ position: "absolute", right: 0, m: 0.5, display: "flex", gap: 1 }}>
                    <Chip
                        label={`vsPar ${prettyParFormat(currentHoleScore?.score, currentHoleScore?.par)}`}
                        sx={{ bgcolor: "primary.500", mr: 8 }}
                    ></Chip>
                </Box>

                <Box
                    sx={{ mt: 2, width: 30, height: 6, bgcolor: "primary.200", borderRadius: 3 }}
                />
            </Box>
            <Box
                sx={{
                    position: "absolute",
                    top: "-60px",
                    p: 0.5,
                    pb: `${NAV_HEIGHT + 16}px`,
                    height: "100%",
                    width: "100%",
                    bgcolor: "primary.300",
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                }}
                onTouchStart={(e) => e.stopPropagation()}
                onTouchMove={(e) => {
                    const target = e.currentTarget;
                    if (target.scrollTop > 0) {
                        e.stopPropagation();
                    }
                }}
            >
                <StyledAnyContentBox
                    sx={{
                        bgcolor: "primary.100",
                        display: "flex",
                        flexDirection: "row",
                        alignItems: "center",
                        m: 0,
                        gap: 0.5,
                        flexGrow: 0,
                        alignSelf: "flex-start",
                        p: 0,
                        ml: "auto",
                        mr: 1,
                    }}
                >
                    <IconButton sx={{ color: "secondary.500" }} onClick={moveToPreviousHole}>
                        <ChevronLeft fontSize="large" />
                    </IconButton>
                    <Box sx={{ textAlign: "center", minWidth: "80px" }}>
                        <Typography
                            variant="caption"
                            color="white"
                            sx={{ display: "block", opacity: 0.7 }}
                        >
                            HOLE
                        </Typography>
                        <Typography
                            variant="h4"
                            sx={{ fontWeight: "800", color: "white", lineHeight: "1em" }}
                        >
                            {selectedHole?.track_number}
                        </Typography>
                    </Box>
                    <IconButton sx={{ color: "secondary.500" }} onClick={moveToNextHole}>
                        <ChevronRight fontSize="large" />
                    </IconButton>
                </StyledAnyContentBox>
                <PlayersHoleScores
                    gameSessionData={gameSessionData}
                    currentTrack={selectedHole?.track_number}
                />
            </Box>
        </SwipeableDrawer>
    );
}
