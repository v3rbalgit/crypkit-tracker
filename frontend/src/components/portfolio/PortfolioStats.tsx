import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

interface PortfolioStatsProps {
  totalValue: number;
  dailyChange?: number;
}

const PortfolioStats: React.FC<PortfolioStatsProps> = ({ totalValue, dailyChange }) => {
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

  const isPositiveChange = dailyChange && dailyChange > 0;

  return (
    <Paper
      component={motion.div}
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
      elevation={2}
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, #1a237e 0%, #283593 50%, #303f9f 100%)',
        color: 'white',
        borderRadius: 2,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background decoration */}
      <Box
        component={motion.div}
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.1 }}
        transition={{ duration: 1 }}
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at top right, rgba(255,255,255,0.2) 0%, transparent 70%)',
        }}
      />

      <Box sx={{ position: 'relative', zIndex: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography
              variant="subtitle1"
              sx={{
                mb: 1,
                opacity: 0.8,
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                fontSize: '0.875rem'
              }}
            >
              Total Portfolio Value
            </Typography>
            <motion.div
              key={totalValue} // Force animation on value change
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
                {formatCurrency(totalValue)}
              </Typography>
            </motion.div>
          </Box>
          {dailyChange !== undefined && (
            <Box
              component={motion.div}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-end',
                gap: 1,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  bgcolor: `${isPositiveChange ? 'success' : 'error'}.main`,
                  px: 2,
                  py: 1,
                  borderRadius: 2,
                  boxShadow: 2,
                }}
              >
                {isPositiveChange ? (
                  <TrendingUpIcon sx={{ mr: 1 }} />
                ) : (
                  <TrendingDownIcon sx={{ mr: 1 }} />
                )}
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  {formatPercentage(dailyChange)}
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                24h Change
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default PortfolioStats;
