import { useGameSession, useSelectedHole } from "#/hooks/GameSessionHooks";
import { createContext, useContext, useMemo } from "react";

const GameSessionContext = createContext({});

// holds current game state for easier access in dependent components.
export function GameSessionContextProvider({ children }) {
    // what we have in hole selection
    const selectedHole = useSelectedHole();
    // returns current session
    const { data: gameSessionData } = useGameSession();

    const contextState = useMemo(() => {
        // todo: make all user data available too
        const gameIdx = gameSessionData?.user_score?.scores.findIndex(
            (val) => val.track_number === selectedHole.track_number,
        );
        if (gameIdx !== -1 && gameIdx !== undefined) {
            return gameSessionData?.user_score?.scores[gameIdx];
        }
        return {};
    }, [gameSessionData, selectedHole]);

    return (
        <GameSessionContext.Provider value={contextState}>{children}</GameSessionContext.Provider>
    );
}

export const useGameState = () => useContext(GameSessionContext);
