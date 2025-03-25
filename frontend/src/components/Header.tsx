import React, { useState } from 'react';
import { AppBar, Button, Toolbar, Typography, CircularProgress } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

interface HeaderProps {
  onRefreshPrices: () => Promise<boolean>;
}

const Header: React.FC<HeaderProps> = ({ onRefreshPrices }) => {
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const handleRefreshClick = async (): Promise<void> => {
    setIsRefreshing(true);
    try {
      await onRefreshPrices();
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          CrypKit Tracker
        </Typography>
        <Button
          color="inherit"
          onClick={handleRefreshClick}
          disabled={isRefreshing}
          startIcon={isRefreshing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
        >
          {isRefreshing ? 'Refreshing...' : 'Refresh Prices'}
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
