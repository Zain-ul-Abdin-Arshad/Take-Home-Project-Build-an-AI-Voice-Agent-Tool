# AI Voice Agent Frontend

A React frontend for the AI Voice Agent system, built with Vite, React Router, and Tailwind CSS.

## Features

- **Dashboard**: Start test calls and view call results
- **Agent Config**: Create and manage AI agent configurations
- **Call Results**: View detailed call logs with structured summaries

## Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on port 8000

## Installation

```bash
cd frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

Build for production:

```bash
npm run build
```

## API Integration

The frontend is configured to proxy API requests to the backend:

- Development: Requests to `/api/*` are proxied to `http://localhost:8000`
- The backend should be running on port 8000

## Pages

### Dashboard (`/`)
- Start test calls with driver information
- View call results in a table format
- Real-time updates when new calls are started

### Agent Config (`/config`)
- Create new agent configurations
- Edit existing configurations
- JSON settings editor with validation

### Call Results (`/results`)
- View all call logs
- Structured summary display
- Full transcript viewing
- Emergency detection highlighting

## Components

- **Navbar**: Navigation between pages
- **ConfigForm**: Agent configuration form with validation
- **CallTriggerForm**: Form to start new test calls
- **ResultsTable**: Display call logs with summaries

## API Endpoints Used

- `POST /api/config` - Create/update agent config
- `GET /api/config/{id}` - Get agent config
- `POST /api/start-call` - Start a new call
- `GET /api/call-logs` - Get all call logs

## Styling

The app uses Tailwind CSS for styling with a clean, professional design.

## Development Notes

- Ensure the backend is running on port 8000 for API proxying.
- Agent configs are loaded as mock data in the dropdown
- Error handling and loading states are implemented throughout
- Form validation includes JSON syntax checking for settings
