# Quantum Trading AI - Frontend

Modern, production-ready React TypeScript frontend for the Quantum Trading AI platform.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Charts**: Recharts

## Features

- 🎨 Modern, responsive UI with dark mode support
- 🔐 Complete authentication system (login, signup, protected routes)
- 📊 Real-time trading signals dashboard
- 💳 Subscription management
- 📈 Interactive charts and data visualization
- 🌙 Dark/Light theme toggle
- 📱 Fully responsive (mobile, tablet, desktop)
- ⚡ Optimized performance with code splitting
- 🎯 Type-safe with TypeScript
- 🧪 Production-ready error handling

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Update environment variables in `.env`:
```
VITE_API_URL=http://localhost:8000/api/v1
```

### Development

Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   ├── layout/          # Layout components (Header, Sidebar)
│   │   └── features/        # Feature-specific components
│   ├── pages/               # Page components
│   ├── store/               # Zustand stores
│   ├── lib/                 # API client and utilities
│   ├── types/               # TypeScript types
│   ├── hooks/               # Custom React hooks
│   └── utils/               # Utility functions
├── public/                  # Static assets
└── Dockerfile              # Docker configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with ESLint

## Docker

Build and run with Docker:
```bash
docker build -t quantum-frontend .
docker run -p 3000:80 quantum-frontend
```

Or use docker-compose from root:
```bash
cd ..
docker-compose up frontend
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | http://localhost:8000/api/v1 |

## Pages

- `/login` - User login
- `/signup` - User registration
- `/dashboard` - Main dashboard with stats and recent signals
- `/signals` - Trading signals list with filters
- `/analysis` - Run quantum analysis
- `/subscription` - Manage subscription plans
- `/performance` - Track trading performance
- `/settings` - User settings

## UI Components

### Base Components
- Button - Multiple variants (primary, secondary, ghost, destructive)
- Input - With icons, labels, and validation
- Card - Flexible card component
- Modal - Accessible modal dialog
- Badge - Status badges
- Toast - Toast notifications
- Loading - Loading states and skeletons
- Table - Data table with sorting/filtering

### Layout Components
- Header - Top navigation with theme toggle and user menu
- Sidebar - Navigation sidebar
- DashboardLayout - Main app layout wrapper

## State Management

### Auth Store (`useAuthStore`)
- User authentication state
- Login/logout functionality
- Protected route handling

### Theme Store (`useThemeStore`)
- Theme switching (light/dark)
- Persistent theme preference

## API Integration

The app uses Axios for API calls with:
- Automatic token injection
- Request/response interceptors
- Error handling
- Token refresh logic

See `src/lib/api.ts` for API client implementation.

## Styling

Tailwind CSS with custom configuration:
- Custom color palette (primary, secondary)
- Dark mode support
- Custom animations
- Responsive utilities

Custom classes in `src/index.css`:
- `.btn-*` - Button variants
- `.input` - Form input styles
- `.badge-*` - Badge variants
- `.card` - Card styles

## License

Proprietary - All rights reserved
