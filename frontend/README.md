# CrypKit Tracker Frontend

A TypeScript React application for tracking cryptocurrency portfolios.

## Features

- View and manage your cryptocurrency portfolio
- Search for coins using the CoinGecko API
- Track portfolio value and performance

## Tech Stack

- React with TypeScript
- Material UI for component library
- React Query for data fetching
- Axios for API communication

## Development Setup

### Prerequisites

- Node.js (v16+)
- npm or yarn
- Backend server running locally

### Local Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server (connects to localhost:8000 for API):
   ```bash
   npm run start:local
   ```

   This will start the React development server on port 3000 and connect to your locally running backend.

### Production Build

To create a production-ready build:

```bash
npm run build
```

## Docker Usage

### Building and Running with Docker Compose

The application is configured to work with Docker Compose out of the box:

```bash
docker-compose up
```

This will:
1. Build the backend service
2. Build the frontend service
3. Start both services along with required databases (PostgreSQL and Redis)

The frontend will be available at http://localhost:3000

### Building Only the Frontend Container

If you need to build just the frontend container:

```bash
docker build -t crypkit-tracker-frontend ./frontend
```

## API Configuration

- The application uses environment variables to determine the API URL:
  - For local development: connects to http://localhost:8000
  - For production/Docker: uses the /api path which is proxied to the backend service

## Project Structure

- `/src/components` - React components
- `/src/services` - API communication
- `/src/types` - TypeScript interfaces
- `/src/App.tsx` - Main application component
- `/src/index.tsx` - Application entry point
