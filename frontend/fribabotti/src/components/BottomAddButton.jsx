import { Fab } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

export default function BottomAddButton({ onClick }) {
    return (
        <Fab
            color="primary"
            aria-label="add"
            onClick={onClick}
            sx={{
                position: "fixed",
                bottom: 16 + 56,
                right: 16,
                zIndex: (theme) => theme.zIndex.speedDial,
            }}
        >
            <AddIcon />
        </Fab>
    );
}
