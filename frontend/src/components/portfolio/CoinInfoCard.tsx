import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import { CoinDetail } from '../../types/coin';

interface CoinInfoCardProps {
  coin: CoinDetail;
  inPopover?: boolean;
}

const CoinInfoCard: React.FC<CoinInfoCardProps> = ({ coin, inPopover = false }) => {
  const formatMarketCap = (value: number | null): string => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatSupply = (value: number | null): string => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      notation: 'compact',
      maximumFractionDigits: 2,
    }).format(value);
  };

  // Calculate supply percentage if both values are available
  const supplyPercentage = coin.circulating_supply && coin.max_supply
    ? (coin.circulating_supply / coin.max_supply) * 100
    : null;

  return (
    <Box
      sx={{
        p: 2,
        width: 300,
        bgcolor: 'background.paper',
        ...(inPopover ? {} : { borderRadius: 2 })
      }}
    >
      {/* Header with image and name */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        {coin.image_url && (
          <img
            src={coin.image_url}
            alt={coin.name}
            style={{
              width: 32,
              height: 32,
              marginRight: 8,
              borderRadius: '50%',
            }}
          />
        )}
        <Box>
          <Typography variant="h6">{coin.name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {coin.symbol.toUpperCase()}
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ my: 1 }} />

      {/* Market Data */}
      <Box sx={{ my: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2" color="text.secondary">
            Market Cap Rank
          </Typography>
          <Typography variant="body2" fontWeight="bold">
            #{coin.market_cap_rank || 'N/A'}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2" color="text.secondary">
            Market Cap
          </Typography>
          <Typography variant="body2">
            {formatMarketCap(coin.market_cap)}
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ my: 1 }} />

      {/* Supply Information */}
      <Box sx={{ my: 1 }}>
        <Box sx={{ mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Supply
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
            <Typography variant="caption">
              Circulating: {formatSupply(coin.circulating_supply)}
            </Typography>
            <Typography variant="caption">
              Max: {formatSupply(coin.max_supply)}
            </Typography>
          </Box>
          {supplyPercentage !== null && (
            <Tooltip title={`${supplyPercentage.toFixed(2)}% of max supply`}>
              <LinearProgress
                variant="determinate"
                value={supplyPercentage}
                sx={{
                  mt: 1,
                  height: 6,
                  borderRadius: 1,
                }}
              />
            </Tooltip>
          )}
        </Box>
      </Box>

      <Divider sx={{ my: 1 }} />

      {/* Description */}
      {coin.description && (
        <Box sx={{ mt: 1 }}>
          <Typography variant="body2" color="text.secondary">
            About
          </Typography>
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              maxHeight: inPopover ? 'none' : '3em',
              overflow: inPopover ? 'auto' : 'hidden',
              ...(inPopover ? {} : {
                WebkitBoxOrient: 'vertical',
                WebkitLineClamp: 3,
                display: '-webkit-box',
              })
            }}
          >
            {coin.description}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default CoinInfoCard;
