import { ListItem, ListItemButton, styled } from "@mui/material";

export const StyledListItem = styled(ListItem)(({ theme }) => ({
    paddingLeft: theme.spacing(0.5),
    paddingRight: theme.spacing(0.5),
    paddingTop: theme.spacing(0.25),
    paddingBottom: theme.spacing(0.25),
}));

export const StyledListItemButton = styled(ListItemButton)(({ theme }) => ({
    paddingLeft: theme.spacing(0.5),
    marginLeft: theme.spacing(0.5),
    marginRight: theme.spacing(0.5),
    marginBottom: theme.spacing(0.5),
    marginTop: theme.spacing(0.5),

    border: "1px solid",
    borderColor: theme.palette.divider,
    borderRadius: "5px",
    backgroundColor: theme.palette.background.paper,
}));
