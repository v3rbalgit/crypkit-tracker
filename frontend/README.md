# CrypKit Tracker Frontend

A TypeScript React application for tracking cryptocurrency portfolios.

## Features

- View and manage your cryptocurrency portfolio
- Search for coins using the CoinGecko API
- Track portfolio value and performance
- Visualize your portfolio allocation with charts

## Quick Start

1. **Prerequisites**
   - Node.js (v16+)
   - npm or yarn
   - Backend server running locally on port 8000

2. **Installation**
   ```bash
   npm install
   ```

3. **Run the app**
   ```bash
   npm start
   ```
   This will start the React development server on port 3000 and automatically connect to your locally running backend.

## How to Use the App

### View Your Portfolio
- On the main screen, you'll see your portfolio with the total value and performance
- The portfolio is organized as a list of coins with their current value and performance
- Use the chart to visualize your portfolio allocation

### Add Coins to Your Portfolio
1. Click on the search bar at the top of the page
2. Type the name or symbol of the cryptocurrency you want to add
3. Select the coin from the dropdown results
4. Enter the amount you own
5. The coin will be added to your portfolio and the total value will be updated

### Manage Your Portfolio
- **Edit Amount**: Click on the amount field for any coin to edit the quantity
- **Remove Coin**: Click the remove button (trash icon) next to any coin to remove it from your portfolio
- **View Details**: Click on any coin to view more detailed information

### Portfolio Stats
- The top section displays your total portfolio value
- You can see the 24h change percentage
- The chart shows the allocation of your portfolio by percentage

## Tech Stack

- React with TypeScript
- Material UI for component library
- React Query for data fetching
- Axios for API communication
- Recharts for data visualization

## Project Structure

- `/src/components` - React components
- `/src/components/portfolio` - Portfolio-specific components
- `/src/services` - API communication
- `/src/types` - TypeScript interfaces
- `/src/styles` - CSS and styling
- `/src/App.tsx` - Main application component
- `/src/index.tsx` - Application entry point

## Development

### Available Scripts

- `npm start` - Starts the development server with API connection to http://localhost:8000
- `npm test` - Runs tests
- `npm run build` - Creates a build for local testing
- `npm run eject` - Ejects from create-react-app (not recommended)

### API Configuration

The application is configured to connect to the local backend server on http://localhost:8000. This is set via the environment variable `REACT_APP_API_BASE_URL` in the start script and the proxy setting in package.json.
