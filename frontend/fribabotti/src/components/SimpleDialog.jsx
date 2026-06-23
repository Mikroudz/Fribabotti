import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    IconButton,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

export default function DeleteConfirmation({ open, onClose, title, contentText, onDelete }) {
    const handleConfirmDelete = () => {
        // Insert your deletion logic / API call here
        console.log("Item deleted successfully.");
        onClose(false);
        if (onDelete) onDelete();
    };

    const handleCancel = () => {
        if (onClose) onClose();
    };

    return (
        <>
            <Dialog
                open={open}
                onClose={onClose}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">{title}</DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">{contentText}</DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCancel} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={handleConfirmDelete} color="error" autoFocus>
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}

export function SimpleDataDialog({ open, onClose, title, children }) {
    return (
        <Dialog
            open={open}
            onClose={onClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
            maxWidth="md"
            slotProps={{ paper: { sx: { ml: 0.5, mr: 0.5 } } }}
        >
            <DialogTitle id="alert-dialog-title">{title}</DialogTitle>
            <IconButton
                aria-label="close"
                onClick={onClose}
                sx={(theme) => ({
                    position: "absolute",
                    right: 8,
                    top: 8,
                    color: theme.palette.grey[500],
                })}
            >
                <CloseIcon />
            </IconButton>
            <DialogContent sx={{ p: 1 }}>{children}</DialogContent>
        </Dialog>
    );
}
