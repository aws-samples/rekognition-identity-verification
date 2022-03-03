import * as React from 'react';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import MenuIcon from '@mui/icons-material/Menu';
import IconButton from '@mui/material/IconButton';
import Box from '@mui/material/Box';
import Avatar from '@mui/material/Avatar';
import Menu from '@mui/material/Menu';
import ListItemIcon from '@mui/material/ListItemIcon';
import Divider from '@mui/material/Divider';
import Tooltip from '@mui/material/Tooltip';
import PersonAdd from '@mui/icons-material/PersonAdd';
import Settings from '@mui/icons-material/Settings';
import Logout from '@mui/icons-material/Logout';
import { API } from "aws-amplify";
import {
   useNavigate
} from "react-router-dom";

export default function RIVMenu() {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);
  // const [resetSuccess, setresetSuccess] = React.useState();
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const clear = () => {
    localStorage.removeItem("pic");
    navigate("/");
    // API.get("identityverification", "/reset").then(response => {
    //   let responseData = response
    //   console.log(responseData)
    //   if (responseData.status === "SUCCEEDED") {
    //     navigate("/");
    //   }
    //   else {
    //     console.log(responseData.status + " : " + responseData.error)
    //   }
    // });
  };

  return (
    <div>
      <Box sx={{ display: 'flex', alignItems: 'center', textAlign: 'center' }}>
        <Tooltip title="Account settings">
          <IconButton
            color="inherit"
            onClick={handleClick}
            size="small"
            sx={{ ml: 2 }}
            aria-controls={open ? 'account-menu' : undefined}
            aria-haspopup="true"
            aria-expanded={open ? 'true' : undefined}
          >
            <MenuIcon></MenuIcon>
          </IconButton>
        </Tooltip>
      </Box>
      <Menu
        anchorEl={anchorEl}
        id="account-menu"
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        PaperProps={{
          elevation: 0,
          sx: {
            overflow: 'visible',
            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
            mt: 1.5,
            '& .MuiAvatar-root': {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
            '&:before': {
              content: '""',
              display: 'block',
              position: 'absolute',
              top: 0,
              right: 14,
              width: 10,
              height: 10,
              bgcolor: 'background.paper',
              transform: 'translateY(-50%) rotate(45deg)',
              zIndex: 0,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem>
          <Button
            color="inherit"
            href="/login">
            <Avatar /> Sign-in
          </Button>
        </MenuItem>
        <Divider />
        <MenuItem>
          <Button
            color="inherit"
            href="/register">
            <ListItemIcon>
              <PersonAdd fontSize="small" />
            </ListItemIcon>
            Register
          </Button>
        </MenuItem>
        <MenuItem>
          <Button
            color="inherit"
            href="/registerwithid">
            <ListItemIcon>
              <Settings fontSize="small" />
            </ListItemIcon>
            Register with ID
          </Button>
        </MenuItem>
        <MenuItem>
          <Button
            color="inherit"
            onClick={clear}>
            <ListItemIcon>
              <Logout fontSize="small" />
            </ListItemIcon>
            Logout
          </Button>
        </MenuItem>
      </Menu>
    </div>
  );
}
