# Contract Intelligence Platform - Frontend

A modern React-based frontend application for the Contract Intelligence Platform, providing an intuitive interface for contract upload, analysis, and management.

## 🚀 Features

- **Modern UI/UX**: Built with React 18, TypeScript, and Tailwind CSS
- **Drag & Drop Upload**: Intuitive file upload interface with progress tracking
- **Real-time Dashboard**: Live contract status updates and statistics
- **Contract Management**: Comprehensive view and management of contract data
- **Responsive Design**: Mobile-first design that works across all devices
- **Advanced Components**: Built with shadcn/ui component library
- **Data Visualization**: Interactive charts and analytics for contract insights
- **File Management**: Secure file upload, download, and preview capabilities

## 🛠️ Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and building
- **Styling**: Tailwind CSS for utility-first styling
- **UI Components**: shadcn/ui (built on Radix UI primitives)
- **State Management**: React Query (TanStack Query) for server state
- **Routing**: React Router v6 for navigation
- **Icons**: Lucide React for consistent iconography
- **Form Handling**: React Hook Form with Zod validation
- **Charts**: Recharts for data visualization

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── favicon.ico        # Application favicon
│   ├── placeholder.svg    # Placeholder images
│   └── robots.txt         # SEO robots file
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Navigation.tsx # Main navigation component
│   │   └── ui/           # shadcn/ui component library
│   ├── pages/            # Application pages/routes
│   │   ├── Dashboard.tsx # Main dashboard view
│   │   ├── Upload.tsx    # Contract upload interface
│   │   ├── ContractDetails.tsx # Detailed contract view
│   │   └── NotFound.tsx  # 404 error page
│   ├── services/         # API client and data fetching
│   │   ├── api.ts        # API service functions
│   │   ├── queries.ts    # React Query hooks
│   │   └── types.ts      # TypeScript type definitions
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility functions
│   ├── App.tsx          # Main application component
│   └── main.tsx         # Application entry point
├── package.json         # Dependencies and scripts
├── tailwind.config.ts   # Tailwind CSS configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite build configuration
```

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **npm** or **bun** package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Technical_Assignment_Contract_Intelligence/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or using bun
   bun install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API configuration
   ```

4. **Start the development server**
   ```bash
   npm run dev
   # or using bun
   bun run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:5173`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:dev` - Build for development environment
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality checks

## 🔧 Development

### Code Quality

This project uses:
- **ESLint** for code linting
- **TypeScript** for type safety
- **Prettier** (recommended) for code formatting

### Component Structure

Components are organized using the shadcn/ui pattern:
- Core UI components in `src/components/ui/`
- Page-specific components in `src/components/`
- Page components in `src/pages/`

### API Integration

The frontend communicates with the backend API using:
- **API Service** (`src/services/api.ts`) for HTTP requests
- **React Query** (`src/services/queries.ts`) for data fetching and caching
- **TypeScript Types** (`src/services/types.ts`) for type safety

## 📱 Features Overview

### Dashboard
- Contract statistics and overview
- Recent uploads and processing status
- Quick actions for common tasks

### Upload Interface
- Drag-and-drop file upload
- Progress tracking for uploads
- File validation and error handling
- Batch upload support

### Contract Details
- Comprehensive contract data display
- Extracted information visualization
- Scoring and gap analysis
- File download capabilities

### Responsive Design
- Mobile-first approach
- Optimized for tablets and desktops
- Touch-friendly interfaces
- Progressive Web App capabilities

## 🏗️ Building for Production

### Build Process

1. **Build the application**
   ```bash
   npm run build
   ```

2. **Preview the build**
   ```bash
   npm run preview
   ```

### Deployment Options

- **Static Hosting**: Deploy to Netlify, Vercel, or AWS S3
- **Docker**: Containerize with the provided Dockerfile
- **CDN**: Use with any Content Delivery Network

### Performance Optimizations

- Code splitting with Vite
- Tree shaking for smaller bundle sizes
- Lazy loading of routes and components
- Optimized asset handling

## 🔒 Security

- Input validation with Zod schemas
- Secure API communication
- CSRF protection considerations
- Content Security Policy ready

## 🧪 Testing

### Running Tests

```bash
npm run test
```

### Testing Strategy

- Unit tests for utility functions
- Component testing with React Testing Library
- Integration tests for user workflows
- End-to-end testing with Playwright (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding standards and run lints
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Coding Standards

- Use TypeScript for all new code
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries
- Write self-documenting code

## 🆘 Support

- Check the API documentation at the backend `/docs` endpoint
- Review component documentation in Storybook (if available)
- Create issues for bugs or feature requests
- Join discussions for general questions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
