import { useState } from 'react';
import { Box, Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';

import Header from './components/Header';
import CoinSearch from './components/CoinSearch';
import Portfolio from './components/Portfolio';
import { portfolioApi } from './services/api';
import { CoinDetail } from './types/coin';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  const [refreshFlag, setRefreshFlag] = useState<number>(0);
  const [selectedCoin, setSelectedCoin] = useState<CoinDetail | null>(null);

  // Handle adding a coin to portfolio
  const handleAddCoin = async (coinId: string, amount: number): Promise<boolean> => {
    try {
      await portfolioApi.addCoin(coinId, amount);
      // Refresh portfolio data
      setRefreshFlag((prev) => prev + 1);
      return true;
    } catch (error) {
      console.error('Error adding coin:', error);
      return false;
    }
  };

  // Handle updating a portfolio entry
  const handleUpdateEntry = async (entryId: number, amount: number): Promise<boolean> => {
    try {
      await portfolioApi.updateEntry(entryId, amount);
      // Refresh portfolio data
      setRefreshFlag((prev) => prev + 1);
      return true;
    } catch (error) {
      console.error('Error updating entry:', error);
      return false;
    }
  };

  // Handle removing a coin from portfolio
  const handleRemoveEntry = async (entryId: number): Promise<boolean> => {
    try {
      await portfolioApi.removeEntry(entryId);
      // Refresh portfolio data
      setRefreshFlag((prev) => prev + 1);
      return true;
    } catch (error) {
      console.error('Error removing entry:', error);
      return false;
    }
  };

  // Handle refreshing coin prices
  const handleRefreshPrices = async (): Promise<boolean> => {
    try {
      await portfolioApi.refreshPrices();
      // Refresh portfolio data
      setRefreshFlag((prev) => prev + 1);
      return true;
    } catch (error) {
      console.error('Error refreshing prices:', error);
      return false;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Header onRefreshPrices={handleRefreshPrices} />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2 }}>
            {/* Left side - Portfolio */}
            <Box sx={{ flex: 1 }}>
              <Portfolio
                refreshFlag={refreshFlag}
                onUpdateEntry={handleUpdateEntry}
                onRemoveEntry={handleRemoveEntry}
                selectedCoin={selectedCoin}
              />
            </Box>

            {/* Right side - Coin Search */}
            <Box sx={{ flex: 1 }}>
              <CoinSearch
                onAddCoin={handleAddCoin}
                onSelectCoin={setSelectedCoin}
                refreshFlag={refreshFlag}
              />
            </Box>
          </Box>
        </Container>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
