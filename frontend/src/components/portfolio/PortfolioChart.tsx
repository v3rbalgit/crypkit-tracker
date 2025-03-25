import React, { useMemo } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { CoinDetail } from '../../types/coin';
import { PortfolioEntryResponse } from '../../types/portfolio';

interface PortfolioChartProps {
  entries: PortfolioEntryResponse[];
  totalValue: number;
  coinDetails?: Map<string, CoinDetail>;
}

const COLORS = ['#2196f3', '#4caf50', '#f44336', '#ff9800', '#9c27b0', '#00bcd4', '#673ab7', '#3f51b5'];

const PortfolioChart: React.FC<PortfolioChartProps> = ({ entries, totalValue, coinDetails }) => {
  // Prepare data for the chart
  const chartData = useMemo(() => {
    return entries
      .filter(entry => entry.current_value_usd && entry.current_value_usd > 0)
      .map((entry, index) => ({
        name: entry.coin.symbol.toUpperCase(),
        value: Number(entry.current_value_usd),
        fill: COLORS[index % COLORS.length],
      }));
  }, [entries]);

  if (!chartData.length) {
    return (
      <Paper
        elevation={2}
        sx={{
          p: 2,
          height: 400,
          borderRadius: 2,
          background: 'linear-gradient(to bottom right, #1a237e, #0d47a1)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="subtitle1">No portfolio data to display</Typography>
      </Paper>
    );
  }

  console.log('Simple Chart Data:', chartData);

  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        height: 400,
        borderRadius: 2,
        background: 'linear-gradient(to bottom right, #1a237e, #0d47a1)',
        color: 'white',
      }}
    >
      <Typography variant="h6" gutterBottom>
        Portfolio Distribution
      </Typography>

      <Box
        sx={{
          height: '320px',
          width: '100%',
          position: 'relative',
        }}
      >
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => `$${Number(value).toLocaleString()}`}
              contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', color: '#333' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default PortfolioChart;
