import { useState } from "react";
import { IconButton, Tooltip } from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CheckIcon from "@mui/icons-material/Check";

export const ClickToCopy = ({ textToCopy }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(textToCopy);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error("Failed to copy text: ", err);
        }
    };

    return (
        <Tooltip title={copied ? "Copied!" : "Copy to clipboard"} placement="top">
            <IconButton onClick={handleCopy} color={copied ? "success" : "default"}>
                {copied ? <CheckIcon /> : <ContentCopyIcon />}
            </IconButton>
        </Tooltip>
    );
};
