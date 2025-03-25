import React, { useState, useCallback } from 'react';
import { Box, Container, Grid } from '@mui/material';
import { useQuery } from 'react-query';

import { portfolioApi } from '../services/api';
import { CoinDetail } from '../types/coin';
import { PortfolioEntryResponse } from '../types/portfolio';
import CoinDetailsManager from './portfolio/CoinDetailsManager';
import PortfolioStats from './portfolio/PortfolioStats';
import PortfolioChart from './portfolio/PortfolioChart';
import PortfolioList from './portfolio/PortfolioList';

interface PortfolioProps {
  refreshFlag?: number;
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
  const [coinDetails, setCoinDetails] = useState<Map<string, CoinDetail>>(new Map());

  const handleDetailsLoaded = useCallback((details: Map<string, CoinDetail>) => {
    setCoinDetails(details);
  }, []);

  // Fetch portfolio summary data using React Query
  const { data: portfolioData, isLoading, error, refetch } = useQuery(
    ['portfolio-summary', refreshFlag],
    portfolioApi.getPortfolioSummary,
    {
      refetchOnWindowFocus: false,
      staleTime: 60000, // 1 minute
    }
  );

  const handleEditEntry = useCallback((entryId: number, amount: number) => {
    return onUpdateEntry(entryId, amount);
  }, [onUpdateEntry]);

  const handleDeleteEntry = useCallback((entryId: number) => {
    onRemoveEntry(entryId);
  }, [onRemoveEntry]);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        Loading portfolio...
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2, textAlign: 'center', color: 'error.main' }}>
        Error loading portfolio data. Please try again.
      </Box>
    );
  }

  if (!portfolioData || portfolioData.entries.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center', color: 'text.secondary' }}>
        Your portfolio is empty. Use the search to add coins.
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      {portfolioData.entries.length > 0 && (
        <CoinDetailsManager
          entries={portfolioData.entries}
          onDetailsLoaded={handleDetailsLoaded}
        />
      )}

      <Grid container spacing={3}>
        {/* Stats Section */}
        <Grid item xs={12}>
          <PortfolioStats
            totalValue={portfolioData.total_value_usd}
            dailyChange={portfolioData.total_24h_change_percentage ?? undefined}
          />
        </Grid>

        {/* Adjusted layout for better space utilization */}
        <Grid container item spacing={3}>
          {/* Chart Section */}
          <Grid item xs={12} lg={5}>
            <PortfolioChart
              entries={portfolioData.entries}
              totalValue={portfolioData.total_value_usd}
              coinDetails={coinDetails}
            />
          </Grid>

          {/* List Section - now with more space */}
          <Grid item xs={12} lg={7}>
            <PortfolioList
              entries={portfolioData.entries}
              totalValue={portfolioData.total_value_usd}
              onEdit={handleEditEntry}
              onDelete={handleDeleteEntry}
              coinDetails={coinDetails}
            />
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Portfolio;
