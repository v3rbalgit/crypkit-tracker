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
}

const CoinSearch: React.FC<CoinSearchProps> = ({ onAddCoin, onSelectCoin, refreshFlag }) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<CoinSearchResponse[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [selectedCoin, setSelectedCoin] = useState<CoinDetail | CoinSearchResponse | null>(null);
  const [addDialogOpen, setAddDialogOpen] = useState<boolean>(false);
  const [amount, setAmount] = useState<string>('');

  const [error, setError] = useState<string | null>(null);

  // Debounced search function
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

  // Handle search input change with debounce
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      debouncedSearch(searchQuery);
    }, 300); // 300ms delay

    return () => clearTimeout(timeoutId);
  }, [searchQuery, debouncedSearch]);

  // Refresh search results when refreshFlag changes
  useEffect(() => {
    if (searchQuery) {
      debouncedSearch(searchQuery);
    }
  }, [refreshFlag, debouncedSearch, searchQuery]);

  // Handle search input change
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchQuery(event.target.value);
    setError(null);
  };

  // Handle selecting a coin
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

  // Handle opening the add dialog
  const handleOpenAddDialog = (coin: CoinSearchResponse): void => {
    setSelectedCoin(coin);
    setAmount('');
    setAddDialogOpen(true);
  };

  // Handle closing the add dialog
  const handleCloseAddDialog = (): void => {
    setAddDialogOpen(false);
  };

  // Handle adding a coin to the portfolio
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
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Search Coins
          </Typography>

          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search for a coin..."
              value={searchQuery}
              onChange={handleSearchChange}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    {searchQuery && (
                      <IconButton
                        aria-label="clear search"
                        onClick={() => {
                          setSearchQuery('');
                          setSearchResults([]);
                        }}
                        edge="end"
                      >
                        <ClearIcon />
                      </IconButton>
                    )}
                    <Box display="flex" alignItems="center">
                      {isSearching ? (
                        <CircularProgress size={24} sx={{ mx: 1 }} />
                      ) : (
                        <SearchIcon sx={{ mx: 1, color: 'action.active' }} />
                      )}
                    </Box>
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {searchResults.length > 0 && (
            <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
              <List dense>
                {searchResults.map((coin) => (
                  <ListItem
                    key={coin.id}
                    button
                    onClick={() => handleSelectCoin(coin)}
                    divider
                  >
                    <ListItemText
                      primary={coin.name}
                      secondary={`Symbol: ${coin.symbol.toUpperCase()}`}
                    />
                    <ListItemSecondaryAction>
                      {!coin.in_portfolio && (
                        <IconButton
                          edge="end"
                          aria-label="add"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenAddDialog(coin);
                          }}
                        >
                          <AddIcon />
                        </IconButton>
                      )}
                      {coin.in_portfolio && (
                        <Typography variant="caption" color="primary">
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
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography color="error">
                {error}
              </Typography>
            </Box>
          )}

          {!isSearching && !error && searchQuery && searchResults.length === 0 && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No coins found matching '{searchQuery}'
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Add Coin Dialog */}
      <Dialog open={addDialogOpen} onClose={handleCloseAddDialog}>
        <DialogTitle>
          Add {selectedCoin?.name} to Portfolio
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
            />
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAddDialog}>Cancel</Button>
          <Button
            onClick={handleAddCoin}
            disabled={!amount || parseFloat(amount) <= 0}
            color="primary"
          >
            Add to Portfolio
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CoinSearch;
