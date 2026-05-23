import { StyledListItem } from "#/components/List";
import { PrettyPar } from "#/components/PrettyPar";
import { GAME_SESSION_KEY } from "#/hooks/GameSessionHooks";
import { updateScore } from "#/utils/api";
import {
    Avatar,
    Box,
    Button,
    IconButton,
    List,
    ListItemAvatar,
    ListItemText,
    styled,
    Typography,
} from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

export const IncDecButton = styled(Button)(() => ({
    fontSize: "24px",
    padding: 0,
    lineHeight: 1.55,
    minWidth: "42px",
    textAlign: "center",
    justifyContent: "center",
}));

function ScoreControl({ score, par, onScoreChangeDone }) {
    const [localScore, setLocalScore] = useState(0);
    const localRef = useRef(0);
    const isUserAction = useRef(false);
    const debounceTimer = useRef(null);

    const handleIncreDecrement = (toAdd) => {
        if (toAdd > 0 || localScore > 0) {
            isUserAction.current = true;
            localRef.current = localScore + toAdd;
            setLocalScore((prev) => prev + toAdd);
            if (debounceTimer.current) {
                clearTimeout(debounceTimer.current);
            }

            debounceTimer.current = setTimeout(() => {
                onScoreChangeDone(localRef.current);
            }, 1000);
        }
    };

    useEffect(() => {
        localRef.current = score;
        setLocalScore(score);
    }, [score]);

    useEffect(() => {
        return () => {
            if (debounceTimer.current) clearTimeout(debounceTimer.current);
        };
    }, []);

    // TODO: make +/- or par -1 0 +1 +2 score selection configurable
    return (
        <Box sx={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 2 }}>
            <IncDecButton variant="contained" size="small" onClick={() => handleIncreDecrement(-1)}>
                -
            </IncDecButton>
            <PrettyPar score={localScore} par={par}></PrettyPar>
            <IncDecButton variant="contained" size="small" onClick={() => handleIncreDecrement(1)}>
                +
            </IncDecButton>
        </Box>
    );
}

function ScoreItem({ userData, currentTrack, gameSessionId }) {
    const score = userData?.scores?.find((val) => val.track_number === currentTrack);
    const queryClient = useQueryClient();

    const { mutate } = useMutation({
        mutationFn: updateScore,
        onSuccess: (data) => {
            console.log(data);
            queryClient.setQueryData([GAME_SESSION_KEY, String(gameSessionId)], (oldSession) => {
                return oldSession
                    ? {
                          ...oldSession,
                          user_score: {
                              ...oldSession?.user_score,
                              scores: oldSession?.user_score?.scores?.map((score) =>
                                  score.track_number === data.track_number
                                      ? { ...score, ...data }
                                      : score,
                              ),
                          },
                      }
                    : {};
            });
        },
    });

    if (!score) return null;

    const handleScoreChange = (score) => {
        // this is debounced
        mutate({
            data: {
                user_id: userData.user_id,
                track_number: currentTrack,
                score: score,
                game_session_id: gameSessionId,
            },
        });
    };

    const [total_score, total_par] = calcTotalFromScores(userData.scores);

    return (
        <StyledListItem
            sx={{ pt: 0, pb: 0 }}
            key={userData.username}
            secondaryAction={
                <ScoreControl
                    score={score.score}
                    par={score.par}
                    onScoreChangeDone={handleScoreChange}
                />
            }
        >
            <ListItemAvatar>
                <Avatar src={userData.photo_url} />
            </ListItemAvatar>
            <ListItemText
                secondary={
                    <>
                        Total{" "}
                        <PrettyPar
                            score={total_score}
                            par={total_par}
                            component="span"
                            wrap={false}
                        />
                    </>
                }
            >
                {userData.username}
            </ListItemText>
        </StyledListItem>
    );
}

export function calcTotalFromScores(scores) {
    if (!Array.isArray(scores)) {
        return [0, 0];
    }
    const res = scores.reduce(
        (acc, val) => {
            if (val.score > 0) {
                acc[0] += val.score;
                acc[1] += val.par;
            }
            return acc;
        },
        [0, 0],
    );
    return res;
}

export function PlayersHoleScores({ gameSessionData, currentTrack }) {
    return (
        <List dense sx={{ m: 1, mt: 0 }}>
            <ScoreItem
                userData={gameSessionData?.user_score}
                currentTrack={currentTrack}
                gameSessionId={gameSessionData?.id}
            />
            {[].map((userData, i) => (
                <ScoreItem
                    key={i}
                    userData={userData}
                    currentTrack={currentTrack}
                    gameSessionId={gameSessionData?.id}
                />
            ))}
        </List>
    );
}
