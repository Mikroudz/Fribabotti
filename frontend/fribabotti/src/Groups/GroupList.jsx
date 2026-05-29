import { StyledListItem, StyledListItemButton } from "#/components/List";
import { StyledAnyContentBox } from "#/components/StyledContentBoxes";
import { useUserGroups } from "#/hooks/ProfileHooks";
import { Route } from "#/routes/groups/$groupId.index";
import { Button, List, ListItemText, Typography } from "@mui/material";
import { Link } from "@tanstack/react-router";
import { Route as NewGroupRoute } from "#/routes/groups/new";

export function GroupList() {
    const { data: groups } = useUserGroups();
    return (
        <StyledAnyContentBox sx={{ position: "relative" }}>
            <Button
                nativeButton={false}
                variant="contained"
                size="small"
                sx={{ bgcolor: "secondary.main", position: "absolute", top: 0, right: 0, m: 0.75 }}
                component={Link}
                to={NewGroupRoute.to}
            >
                New Group
            </Button>
            <Typography>Groups</Typography>
            <List>
                {groups?.map((val) => (
                    <StyledListItem
                        key={val.id}
                        sx={{ alignItems: "center", bgcolor: "background.default", mb: 1, pb: 0 }}
                    >
                        <StyledListItemButton
                            component={Link}
                            to={Route.to}
                            params={{ groupId: val.id }}
                            from={location.pathname}
                        >
                            <ListItemText primary={val?.name} />
                        </StyledListItemButton>
                    </StyledListItem>
                ))}
            </List>
        </StyledAnyContentBox>
    );
}
