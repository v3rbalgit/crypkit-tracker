import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  Paper,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  OutlinedInput,
  ListItemSecondaryAction,
  Tooltip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import ClearIcon from '@mui/icons-material/Clear';

import { coinApi } from '../services/api';
import { CoinDetail, CoinSearchResponse } from '../types/coin';

interface CoinSearchProps {
  onAddCoin: (coinId: string, amount: number) => Promise<boolean>;
  onSelectCoin?: (coin: CoinDetail | null) => void;
  refreshFlag?: number;
  inHeader?: boolean;
}

const CoinSearch: React.FC<CoinSearchProps> = ({ onAddCoin, onSelectCoin, refreshFlag, inHeader = false }) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<CoinSearchResponse[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [selectedCoin, setSelectedCoin] = useState<CoinDetail | CoinSearchResponse | null>(null);
  const [addDialogOpen, setAddDialogOpen] = useState<boolean>(false);
  const [amount, setAmount] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const debouncedSearch = useCallback(
    async (query: string) => {
      if (!query.trim()) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      setError(null);

      try {
        const data = await coinApi.searchCoins(query);
        setSearchResults(data.results || []);
      } catch (error) {
        console.error('Error searching for coins:', error);
        setError('Failed to search coins. Please try again.');
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    },
    [refreshFlag]
  );

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      debouncedSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, debouncedSearch]);

  useEffect(() => {
    if (searchQuery) {
      debouncedSearch(searchQuery);
    }
  }, [refreshFlag, debouncedSearch, searchQuery]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchQuery(event.target.value);
    setError(null);
  };

  const handleSelectCoin = async (coin: CoinSearchResponse): Promise<void> => {
    try {
      const coinDetails = await coinApi.getCoin(coin.id);
      setSelectedCoin({ ...coin, ...coinDetails });
      if (onSelectCoin) {
        onSelectCoin({ ...coin, ...coinDetails });
      }
    } catch (error) {
      console.error('Error fetching coin details:', error);
    }
  };

  const handleOpenAddDialog = (coin: CoinSearchResponse): void => {
    setSelectedCoin(coin);
    setAmount('');
    setAddDialogOpen(true);
  };

  const handleCloseAddDialog = (): void => {
    setAddDialogOpen(false);
  };

  const handleAddCoin = async (): Promise<void> => {
    if (!selectedCoin || !amount || parseFloat(amount) <= 0) return;

    try {
      const success = await onAddCoin(selectedCoin.id, parseFloat(amount));
      if (success) {
        handleCloseAddDialog();
      }
    } catch (error) {
      console.error('Error adding coin to portfolio:', error);
    }
  };

  return (
    <div>
      <Card
        sx={{
          borderRadius: inHeader ? 0 : 3,
          overflow: 'hidden',
          boxShadow: inHeader ? 'none' : (theme) => `0 8px 32px ${theme.palette.primary.main}20`,
          height: inHeader ? 'auto' : 'initial',
        }}
      >
        <CardContent sx={{ p: 3 }}>
          {!inHeader && (
            <Typography variant="h6" gutterBottom sx={{
              fontWeight: 600,
              background: 'linear-gradient(45deg, #1a237e, #303f9f)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 3,
            }}>
              Search Coins
            </Typography>
          )}

          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search by name or symbol..."
              value={searchQuery}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: 'action.active' }} />
                  </InputAdornment>
                ),
                endAdornment: searchQuery && (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setSearchQuery('')}
                      size="small"
                      sx={{ mr: 0.5 }}
                    >
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.01)',
                  },
                  '&.Mui-focused': {
                    boxShadow: (theme) => `0 0 0 2px ${theme.palette.primary.main}40`,
                  },
                },
              }}
            />
          </Box>

          {searchResults.length > 0 && (
            <Paper
              variant="outlined"
              sx={{
                maxHeight: 400,
                overflow: 'auto',
                bgcolor: 'background.default',
                borderRadius: 2,
              }}
            >
              <List>
                {searchResults.map((coin) => (
                  <ListItem
                    key={coin.id}
                    button
                    onClick={() => handleSelectCoin(coin)}
                    sx={{
                      py: 2,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                          {coin.name}
                        </Typography>
                      }
                      secondary={coin.symbol.toUpperCase()}
                    />
                    <ListItemSecondaryAction>
                      {!coin.in_portfolio ? (
                        <Tooltip title="Add to portfolio">
                          <IconButton
                            edge="end"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenAddDialog(coin);
                            }}
                            sx={{
                              color: 'primary.main',
                              '&:hover': {
                                bgcolor: 'primary.main',
                                color: 'white',
                              },
                            }}
                          >
                            <AddIcon />
                          </IconButton>
                        </Tooltip>
                      ) : (
                        <Typography
                          variant="caption"
                          sx={{
                            color: 'success.main',
                            bgcolor: 'success.light',
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                            fontWeight: 500,
                          }}
                        >
                          In Portfolio
                        </Typography>
                      )}
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}

          {isSearching && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}

          {error && (
            <Typography color="error" align="center" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}

          {!isSearching && !error && searchQuery && searchResults.length === 0 && (
            <Typography color="text.secondary" align="center" sx={{ mt: 2 }}>
              No coins found matching '{searchQuery}'
            </Typography>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={addDialogOpen}
        onClose={handleCloseAddDialog}
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: (theme) => `0 8px 32px ${theme.palette.primary.main}20`,
          },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Add {selectedCoin?.name} to Portfolio
          </Typography>
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth variant="outlined" margin="normal">
            <InputLabel htmlFor="amount">Amount</InputLabel>
            <OutlinedInput
              id="amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              label="Amount"
              inputProps={{ step: 'any', min: '0' }}
              autoFocus
              sx={{
                borderRadius: 1.5,
              }}
            />
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleCloseAddDialog} variant="outlined">
            Cancel
          </Button>
          <Button
            onClick={handleAddCoin}
            disabled={!amount || parseFloat(amount) <= 0}
            variant="contained"
            sx={{
              px: 3,
              bgcolor: 'primary.main',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
            }}
          >
            Add to Portfolio
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default CoinSearch;
