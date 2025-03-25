import { useEffect, useRef, useMemo } from 'react';
import { useQueries, UseQueryResult } from 'react-query';
import { CoinDetail } from '../../types/coin';
import { PortfolioEntryResponse } from '../../types/portfolio';
import { coinApi } from '../../services/api';

interface CoinDetailsManagerProps {
  entries: PortfolioEntryResponse[];
  onDetailsLoaded: (details: Map<string, CoinDetail>) => void;
}

const CoinDetailsManager: React.FC<CoinDetailsManagerProps> = ({
  entries,
  onDetailsLoaded,
}) => {
  // Create parallel queries for each coin's details
  const queryResults = useQueries(
    entries.map((entry) => ({
      queryKey: ['coinDetails', entry.coin.id],
      queryFn: () => coinApi.getCoin(entry.coin.id),
      staleTime: 60000, // Consider data fresh for 1 minute
      cacheTime: 300000, // Keep in cache for 5 minutes
    }))
  ) as UseQueryResult<CoinDetail, unknown>[];

  // Create a memoized details map to avoid unnecessary updates
  const detailsMap = useMemo(() => {
    const details = new Map<string, CoinDetail>();
    queryResults.forEach((result, index) => {
      if (result.data && entries[index]) {
        const coinId = entries[index].coin.id;
        details.set(coinId, result.data);
      }
    });
    return details;
  }, [queryResults, entries]);

  // Use a ref to track if we've already called onDetailsLoaded with the same data
  const previousDetailsRef = useRef<string>('');

  // Update parent component with details when available, but only when data actually changes
  useEffect(() => {
    // Only update if there's data and it's different from previous data
    if (detailsMap.size > 0) {
      // Create a string representation of details for comparison
      const detailsString = JSON.stringify(Array.from(detailsMap.entries()));

      // Only update if details have changed
      if (detailsString !== previousDetailsRef.current) {
        previousDetailsRef.current = detailsString;
        onDetailsLoaded(detailsMap);
      }
    }
  }, [detailsMap, onDetailsLoaded]);

  // This component doesn't render anything
  return null;
};

export default CoinDetailsManager;
