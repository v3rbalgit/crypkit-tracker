import React, { useState } from 'react';
import {
  AppBar,
  Button,
  Toolbar,
  Typography,
  CircularProgress,
  Box,
  IconButton,
  Popover,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import RefreshIcon from '@mui/icons-material/Refresh';
import WalletIcon from '@mui/icons-material/AccountBalanceWallet';
import SearchIcon from '@mui/icons-material/Search';
import CoinSearch from './CoinSearch';
import { CoinDetail } from '../types/coin';

interface HeaderProps {
  onRefreshPrices: () => Promise<boolean>;
  onAddCoin: (coinId: string, amount: number) => Promise<boolean>;
  onSelectCoin?: (coin: CoinDetail | null) => void;
  refreshFlag?: number;
}

const Header: React.FC<HeaderProps> = ({
  onRefreshPrices,
  onAddCoin,
  onSelectCoin,
  refreshFlag
}) => {
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [searchAnchorEl, setSearchAnchorEl] = useState<HTMLButtonElement | null>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleSearchClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setSearchAnchorEl(event.currentTarget);
  };

  const handleSearchClose = () => {
    setSearchAnchorEl(null);
  };

  const handleRefreshClick = async (): Promise<void> => {
    setIsRefreshing(true);
    try {
      await onRefreshPrices();
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <AppBar
      position="static"
      sx={{
        background: 'linear-gradient(135deg, #1a237e 0%, #283593 50%, #303f9f 100%)',
        boxShadow: (theme) => `0 4px 20px ${theme.palette.primary.dark}40`,
      }}
    >
      <Toolbar>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            flexGrow: 1,
          }}
        >
          <motion.div
            initial={{ rotate: 0 }}
            animate={{ rotate: [0, -10, 10, -10, 0] }}
            transition={{ duration: 0.5, delay: 1 }}
          >
            <WalletIcon sx={{ fontSize: 28 }} />
          </motion.div>
          <Typography
            variant="h6"
            component={motion.div}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            sx={{
              fontWeight: 700,
              letterSpacing: '0.1em',
              background: 'linear-gradient(45deg, #fff 30%, #e3f2fd 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            CrypKit Tracker
          </Typography>
        </Box>

        {/* Search Button */}
        <Box sx={{ mr: 2 }}>
          <IconButton
            color="inherit"
            onClick={handleSearchClick}
            sx={{
              background: 'rgba(255, 255, 255, 0.1)',
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.2)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            <SearchIcon />
          </IconButton>
          <Popover
            open={Boolean(searchAnchorEl)}
            anchorEl={searchAnchorEl}
            onClose={handleSearchClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                width: isMobile ? '90vw' : 400,
                mt: 1,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
                borderRadius: 2,
                overflow: 'hidden',
              },
            }}
          >
            <CoinSearch
              onAddCoin={onAddCoin}
              onSelectCoin={onSelectCoin}
              refreshFlag={refreshFlag}
              inHeader={true}
            />
          </Popover>
        </Box>

        {/* Refresh Button */}
        <AnimatePresence mode="wait">
          <motion.div
            key={isRefreshing ? 'refreshing' : 'idle'}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            <Button
              variant="contained"
              onClick={handleRefreshClick}
              disabled={isRefreshing}
              sx={{
                px: 3,
                py: 1,
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                '&:hover': {
                  background: 'rgba(255, 255, 255, 0.2)',
                },
                transition: 'all 0.3s ease',
              }}
              startIcon={
                isRefreshing ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <RefreshIcon />
                )
              }
            >
              {isRefreshing ? 'Refreshing...' : 'Refresh Prices'}
            </Button>
          </motion.div>
        </AnimatePresence>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
