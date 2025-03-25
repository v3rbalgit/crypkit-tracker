import React, { useState, useMemo } from 'react';
import {
  Box,
  IconButton,
  List,
  ListItem,
  Paper,
  Tooltip,
  Typography,
  Avatar,
  LinearProgress,
  Popover,
  Button,
  ButtonGroup,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import SortIcon from '@mui/icons-material/Sort';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import { CoinDetail } from '../../types/coin';
import { PortfolioEntryResponse } from '../../types/portfolio';
import CoinInfoCard from './CoinInfoCard';
import EditAmountField from './EditAmountField';

interface PortfolioListProps {
  entries: PortfolioEntryResponse[];
  totalValue: number;
  onEdit: (entryId: number, amount: number) => Promise<boolean>;
  onDelete: (entryId: number) => void;
  coinDetails: Map<string, CoinDetail>;
}

interface InfoCardAnchor {
  element: HTMLElement;
  coinId: string;
}

const PortfolioList: React.FC<PortfolioListProps> = ({
  entries,
  totalValue,
  onEdit,
  onDelete,
  coinDetails,
}) => {
  type SortField = 'value' | 'name' | 'change';
  type SortDirection = 'asc' | 'desc';

  interface SortConfig {
    field: SortField;
    direction: SortDirection;
  }

  const [infoCardAnchor, setInfoCardAnchor] = useState<InfoCardAnchor | null>(null);
  const [sortConfig, setSortConfig] = useState<SortConfig>({ field: 'value', direction: 'desc' });
  const [editingEntryId, setEditingEntryId] = useState<number | null>(null);

  const handleCoinClick = (event: React.MouseEvent<HTMLDivElement>, coinId: string) => {
    // Toggle info card - close if the same coin is clicked again
    if (infoCardAnchor && infoCardAnchor.coinId === coinId) {
      setInfoCardAnchor(null);
    } else {
      setInfoCardAnchor({
        element: event.currentTarget,
        coinId,
      });
    }
  };

  const handleHideInfo = () => {
    setInfoCardAnchor(null);
  };

  const handleStartEdit = (entryId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setEditingEntryId(entryId);
  };

  const handleSaveEdit = async (entryId: number, newAmount: number) => {
    try {
      await onEdit(entryId, newAmount);
      setEditingEntryId(null);
    } catch (error) {
      console.error('Error updating amount:', error);
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercentage = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value / 100);
  };

  // Sort entries based on current configuration
  const sortedEntries = useMemo(() => {
    const sorted = [...entries];
    sorted.sort((a, b) => {
      let comparison = 0;
      switch (sortConfig.field) {
        case 'value':
          comparison = (a.current_value_usd || 0) - (b.current_value_usd || 0);
          break;
        case 'name':
          comparison = a.coin.name.localeCompare(b.coin.name);
          break;
        case 'change':
          comparison = (a.coin.price_change_percentage_24h || 0) - (b.coin.price_change_percentage_24h || 0);
          break;
      }
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });
    return sorted;
  }, [entries, sortConfig]);

  const handleSort = (field: SortField) => {
    setSortConfig((current) => ({
      field,
      direction: current.field === field && current.direction === 'desc' ? 'asc' : 'desc',
    }));
  };

  return (
    <Box>
      <Paper
        component={motion.div}
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        elevation={2}
        sx={{ borderRadius: 2 }}
      >
        {/* Header section */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" gutterBottom>
            Portfolio Assets
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              {entries.length} {entries.length === 1 ? 'asset' : 'assets'} in portfolio
            </Typography>
            <ButtonGroup size="small" aria-label="sort options">
              <Button
                onClick={() => handleSort('value')}
                variant={sortConfig.field === 'value' ? 'contained' : 'outlined'}
                endIcon={sortConfig.field === 'value' && (
                  sortConfig.direction === 'asc' ? <ArrowUpwardIcon /> : <ArrowDownwardIcon />
                )}
              >
                Value
              </Button>
              <Button
                onClick={() => handleSort('name')}
                variant={sortConfig.field === 'name' ? 'contained' : 'outlined'}
                endIcon={sortConfig.field === 'name' && (
                  sortConfig.direction === 'asc' ? <ArrowUpwardIcon /> : <ArrowDownwardIcon />
                )}
              >
                Name
              </Button>
              <Button
                onClick={() => handleSort('change')}
                variant={sortConfig.field === 'change' ? 'contained' : 'outlined'}
                endIcon={sortConfig.field === 'change' && (
                  sortConfig.direction === 'asc' ? <ArrowUpwardIcon /> : <ArrowDownwardIcon />
                )}
              >
                Change
              </Button>
            </ButtonGroup>
          </Box>
        </Box>
        <List sx={{ width: '100%', p: 0 }}>
          <AnimatePresence>
            {sortedEntries.map((entry) => {
              const percentage = ((entry.current_value_usd || 0) / totalValue) * 100;
              const priceChange = entry.coin.price_change_percentage_24h || 0;
              const isPositiveChange = priceChange > 0;
              const isEditing = editingEntryId === entry.id;

              return (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ duration: 0.3 }}
                >
                  <ListItem
                    sx={{
                      p: 2,
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                      {/* Header row */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Box sx={{
                          display: 'flex',
                          alignItems: 'center',
                          minWidth: 0,
                          flexShrink: 1
                        }}>
                          {coinDetails.get(entry.coin.id)?.image_url ? (
                            <Avatar
                              src={coinDetails.get(entry.coin.id)!.image_url!}
                              alt={entry.coin.name}
                              sx={{ width: 24, height: 24, mr: 1 }}
                            />
                          ) : (
                            <Avatar
                              sx={{
                                width: 24,
                                height: 24,
                                mr: 1,
                                bgcolor: 'primary.main',
                                fontSize: '12px',
                              }}
                            >
                              {entry.coin.symbol.substring(0, 2).toUpperCase()}
                            </Avatar>
                          )}
                          <Box
                            onClick={(e) => handleCoinClick(e, entry.coin.id)}
                            sx={{ cursor: 'pointer' }}
                          >
                            <Typography
                              variant="subtitle1"
                              sx={{
                                fontWeight: 'bold',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                maxWidth: { xs: '120px', sm: '150px', md: '200px' }
                              }}
                            >
                              {entry.coin.name}
                            </Typography>
                          </Box>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ ml: 1 }}
                          >
                            {entry.coin.symbol.toUpperCase()}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              color: isPositiveChange ? 'success.main' : 'error.main',
                              bgcolor: isPositiveChange ? 'success.light' : 'error.light',
                              px: 1,
                              py: 0.5,
                              borderRadius: 1,
                            }}
                          >
                            {isPositiveChange ? (
                              <TrendingUpIcon sx={{ fontSize: 16, mr: 0.5 }} />
                            ) : (
                              <TrendingDownIcon sx={{ fontSize: 16, mr: 0.5 }} />
                            )}
                            <Typography variant="body2">
                              {formatPercentage(priceChange)}
                            </Typography>
                          </Box>
                          <Tooltip title="Edit Amount">
                            <IconButton
                              size="small"
                              onClick={(e) => handleStartEdit(entry.id, e)}
                              sx={{ '&:hover': { color: 'primary.main' } }}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Remove">
                            <IconButton
                              size="small"
                              onClick={() => onDelete(entry.id)}
                              sx={{ '&:hover': { color: 'error.main' } }}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>

                      {/* Details row - improved to prevent overflow */}
                      <Box sx={{
                        display: 'flex',
                        flexDirection: { xs: 'column', sm: 'row' },
                        justifyContent: 'space-between',
                        mb: 1,
                        gap: 1
                      }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" color="text.secondary" sx={{ mr: 1, flexShrink: 0 }}>
                            Amount:
                          </Typography>
                          {isEditing ? (
                            <EditAmountField
                              initialValue={entry.amount}
                              onSave={(value) => handleSaveEdit(entry.id, value)}
                              onCancel={() => setEditingEntryId(null)}
                            />
                          ) : (
                            <Typography variant="body2" noWrap sx={{ maxWidth: '100%' }}>
                              {entry.amount.toLocaleString()}
                            </Typography>
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          Price: {formatCurrency(entry.coin.current_price || 0)}
                        </Typography>
                        <Typography variant="body2" fontWeight="bold" sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          Value: {formatCurrency(entry.current_value_usd || 0)}
                        </Typography>
                      </Box>

                      {/* Portfolio percentage bar */}
                      <Box sx={{ width: '100%', mt: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Portfolio Share
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {percentage.toFixed(2)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={percentage}
                          sx={{
                            height: 4,
                            borderRadius: 2,
                            bgcolor: 'action.hover',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: isPositiveChange ? 'success.main' : 'error.main',
                            },
                          }}
                        />
                      </Box>
                    </Box>
                  </ListItem>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </List>
      </Paper>
      <Popover
        open={!!infoCardAnchor}
        anchorEl={infoCardAnchor?.element}
        onClose={handleHideInfo}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        // Use click for popover - more stable than hover
        disableRestoreFocus
        slotProps={{
          paper: {
            sx: {
              mt: 1,
              boxShadow: (theme) => theme.shadows[4],
              borderRadius: 2,
              overflow: 'auto',
              maxHeight: 400
            }
          }
        }}
      >
        {infoCardAnchor && coinDetails.get(infoCardAnchor.coinId) && (
          <CoinInfoCard coin={coinDetails.get(infoCardAnchor.coinId)!} inPopover={true} />
        )}
      </Popover>
    </Box>
  );
};

export default PortfolioList;
