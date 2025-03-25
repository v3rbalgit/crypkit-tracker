import React, { useState } from 'react';
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
  Divider,
  FormControl,
  IconButton,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  OutlinedInput,
  Paper,
  Tooltip,
  Typography,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import { useQuery } from 'react-query';

import { portfolioApi } from '../services/api';
import { CoinDetail } from '../types/coin';
import { PortfolioEntryResponse } from '../types/portfolio';

interface PortfolioProps {
  refreshFlag: number;
  onUpdateEntry: (entryId: number, amount: number) => Promise<boolean>;
  onRemoveEntry: (entryId: number) => Promise<boolean>;
  selectedCoin: CoinDetail | null;
}

const Portfolio: React.FC<PortfolioProps> = ({
  refreshFlag,
  onUpdateEntry,
  onRemoveEntry,
  selectedCoin
}) => {
  const [updateDialogOpen, setUpdateDialogOpen] = useState<boolean>(false);
  const [selectedEntry, setSelectedEntry] = useState<PortfolioEntryResponse | null>(null);
  const [amount, setAmount] = useState<string>('');

  // Fetch portfolio summary data
  const { data: portfolioData, isLoading, error, refetch } = useQuery(
    ['portfolio-summary', refreshFlag],
    portfolioApi.getPortfolioSummary,
    {
      refetchOnWindowFocus: false,
      staleTime: 60000, // 1 minute
    }
  );

  // Handle opening the update dialog
  const handleOpenUpdateDialog = (entry: PortfolioEntryResponse): void => {
    setSelectedEntry(entry);
    setAmount(entry.amount.toString());
    setUpdateDialogOpen(true);
  };

  // Handle closing the update dialog
  const handleCloseUpdateDialog = (): void => {
    setUpdateDialogOpen(false);
  };

  // Handle updating a portfolio entry
  const handleUpdateEntry = async (): Promise<void> => {
    if (!selectedEntry || !amount || parseFloat(amount) <= 0) return;

    try {
      const success = await onUpdateEntry(selectedEntry.id, parseFloat(amount));
      if (success) {
        handleCloseUpdateDialog();
        refetch();
      }
    } catch (error) {
      console.error('Error updating portfolio entry:', error);
    }
  };

  // Handle removing a portfolio entry
  const handleRemoveEntry = async (entryId: number): Promise<void> => {
    try {
      const success = await onRemoveEntry(entryId);
      if (success) {
        refetch();
      }
    } catch (error) {
      console.error('Error removing portfolio entry:', error);
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatNumber = (value: number): string => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  return (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Portfolio
          </Typography>

          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography color="error">
                Error loading portfolio data. Please try again.
              </Typography>
            </Box>
          ) : portfolioData?.entries?.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography color="text.secondary">
                Your portfolio is empty. Use the search to add coins.
              </Typography>
            </Box>
          ) : (
            <Box>
              {/* Portfolio Summary */}
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  mb: 3,
                  bgcolor: 'primary.light',
                  color: 'primary.contrastText',
                }}
              >
                <Typography variant="h6">Total Value</Typography>
                <Typography variant="h4">
                  {formatCurrency(portfolioData?.total_value_usd || 0)}
                </Typography>
              </Paper>

              {/* Portfolio Entries */}
              <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
                {portfolioData?.entries.map((entry) => (
                  <React.Fragment key={entry.id}>
                    <ListItem
                      alignItems="flex-start"
                      secondaryAction={
                        <Box>
                          <Tooltip title="Edit Amount">
                            <IconButton
                              edge="end"
                              aria-label="edit"
                              onClick={() => handleOpenUpdateDialog(entry)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Remove">
                            <IconButton
                              edge="end"
                              aria-label="delete"
                              onClick={() => handleRemoveEntry(entry.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      }
                    >
                      <ListItemText
                        primary={
                          <Typography
                            variant="subtitle1"
                            component="div"
                            color="primary"
                          >
                            {entry.coin.name} ({entry.coin.symbol.toUpperCase()})
                          </Typography>
                        }
                        secondary={
                          <React.Fragment>
                            <Typography
                              variant="body2"
                              color="text.primary"
                              component="span"
                            >
                              Amount: {formatNumber(entry.amount)}
                            </Typography>
                            <br />
                            <Typography
                              variant="body2"
                              color="text.primary"
                              component="span"
                            >
                              Price: {formatCurrency(entry.coin.current_price || 0)}
                            </Typography>
                            <br />
                            <Typography
                              variant="body2"
                              color="text.primary"
                              component="span"
                            >
                              Value: {formatCurrency(entry.current_value_usd || 0)}
                            </Typography>
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Update Entry Dialog */}
      <Dialog open={updateDialogOpen} onClose={handleCloseUpdateDialog}>
        <DialogTitle>
          Update {selectedEntry?.coin?.name} Amount
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
          <Button onClick={handleCloseUpdateDialog}>Cancel</Button>
          <Button
            onClick={handleUpdateEntry}
            disabled={!amount || parseFloat(amount) <= 0}
            color="primary"
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Portfolio;
