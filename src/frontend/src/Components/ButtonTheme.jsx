import Button from '@mui/material/Button';
import { styled } from "@mui/material/styles";

const StyledButton = styled(Button)(() => ({
  backgroundColor: "#ff9900",
  "&:hover": {
    backgroundColor: "#ff6633",

  },
  // padding: "10px",
  marginBottom: "20px !important",
  marginTop: "20px !important",
  marginRight: "10px",
  marginLeft: "10px",
  // width: "50%",
  align: "center",
  textAlign: "center"
}));

export default StyledButton;