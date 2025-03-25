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

// Create theme with custom components and palette
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      light: '#303f9f',
      main: '#1a237e',
      dark: '#000051',
      contrastText: '#ffffff',
    },
    secondary: {
      light: '#f73378',
      main: '#f50057',
      dark: '#ab003c',
      contrastText: '#ffffff',
    },
    success: {
      main: '#4caf50',
      light: 'rgba(76, 175, 80, 0.1)',
    },
    error: {
      main: '#f44336',
      light: 'rgba(244, 67, 54, 0.1)',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  components: {
    MuiPaper: {
      defaultProps: {
        elevation: 2,
      },
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          overflow: 'hidden',
        },
      },
    },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', 'Helvetica', 'Arial', sans-serif",
    h6: {
      fontWeight: 600,
    },
    subtitle1: {
      fontWeight: 500,
    },
    button: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
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

  // Handle updating a portfolio entry with optimistic updates
  const handleUpdateEntry = async (entryId: number, amount: number): Promise<boolean> => {
    try {
      const response = await portfolioApi.updateEntry(entryId, amount);
      // Only refresh if API call was successful
      if (response) {
        setRefreshFlag((prev) => prev + 1);
      }
      return !!response;
    } catch (error) {
      console.error('Error updating entry:', error);
      return false;
    }
  };

  // Handle removing a coin from portfolio with optimistic updates
  const handleRemoveEntry = async (entryId: number): Promise<boolean> => {
    try {
      const response = await portfolioApi.removeEntry(entryId);
      // Only refresh if API call was successful
      if (response.detail) {
        setRefreshFlag((prev) => prev + 1);
      }
      return !!response.detail;
    } catch (error) {
      console.error('Error removing entry:', error);
      return false;
    }
  };

  // Handle refreshing coin prices with UI feedback
  const handleRefreshPrices = async (): Promise<boolean> => {
    try {
      const response = await portfolioApi.refreshPrices();
      // Only refresh if API call was successful
      if (response.detail) {
        setRefreshFlag((prev) => prev + 1);
      }
      return !!response.detail;
    } catch (error) {
      console.error('Error refreshing prices:', error);
      return false;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Header
          onRefreshPrices={handleRefreshPrices}
          onAddCoin={handleAddCoin}
          onSelectCoin={setSelectedCoin}
          refreshFlag={refreshFlag}
        />
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          {/* Full width Portfolio */}
          <Portfolio
            refreshFlag={refreshFlag}
            onUpdateEntry={handleUpdateEntry}
            onRemoveEntry={handleRemoveEntry}
            selectedCoin={selectedCoin}
          />
        </Container>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
