import * as React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
// import theme from './Theme';
import Layout from './Layout'

export default function Paperbase() {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    // <ThemeProvider theme={theme}>
    //     <CssBaseline />
            <Layout />
    // </ThemeProvider >
  );
}