import { ListItem, ListItemButton, styled } from "@mui/material";

export const StyledListItem = styled(ListItem)(({ theme }) => ({
    marginBottom: theme.spacing(1),
    paddingLeft: theme.spacing(0.5),
    paddingRight: theme.spacing(0.5),
    paddingTop: theme.spacing(0),
    paddingBottom: theme.spacing(0),

    border: "1px solid",
    borderColor: theme.palette.divider,
    borderRadius: "5px",
    backgroundColor: theme.palette.background.paper,
}));

export const StyledListItemButton = styled(ListItemButton)(({ theme }) => ({
    paddingLeft: theme.spacing(0.5),
    paddingRight: theme.spacing(0.5),
    paddingTop: theme.spacing(0.5),
    paddingBottom: theme.spacing(0.5),
}));
