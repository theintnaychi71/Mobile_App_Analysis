# Mobile App Analysis Frontend

A beautiful React frontend with Google Play Store theme for the Mobile App Market Analysis Dashboard.

## 🚀 Features

- **Google Play Store Theme**: Modern, clean UI inspired by Google Play Store design
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Interactive Dashboard**: Real-time data visualization with beautiful charts
- **Category Analysis**: Explore app distribution across different categories
- **Market Insights**: Key metrics and trends at a glance
- **Modern Tech Stack**: React 18, Vite, Tailwind CSS, Recharts

## 📋 Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API running on `http://localhost:5000`

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── HomePage.jsx      # Landing page with features overview
│   │   └── Dashboard.jsx     # Main dashboard with charts and stats
│   ├── api/
│   │   └── api.js            # API integration layer
│   ├── App.jsx               # Main app component with routing
│   ├── main.jsx              # Entry point
│   └── index.css             # Global styles with Tailwind
├── index.html                # HTML template
├── package.json              # Dependencies
├── tailwind.config.js        # Tailwind configuration
├── vite.config.js            # Vite configuration
└── postcss.config.js         # PostCSS configuration
```

## 🎨 Design System

### Colors (Google Play Store Theme)
- **Google Green**: `#0F9D58`
- **Google Blue**: `#4285F4`
- **Google Yellow**: `#F4B400`
- **Google Red**: `#DB4437`
- **Play Dark**: `#202124`
- **Play Card**: `#1F1F1F`
- **Play Surface**: `#28292C`

### Typography
- **Primary Font**: Google Sans, Roboto, Arial, sans-serif

## 🔌 API Integration

The frontend connects to the Flask backend API at `http://localhost:5000`:

- `GET /api/dashboard/stats` - Main dashboard statistics
- `GET /api/category-analysis` - Category-wise analysis
- `GET /health` - Health check endpoint

## 📊 Dashboard Features

### Key Metrics
- Total Apps analyzed
- Average Rating across all apps
- Total Installs
- Free vs Paid app percentage

### Visualizations
- **Category Distribution**: Bar chart showing top categories by app count
- **Free vs Paid**: Pie chart showing monetization model distribution
- **Rating Distribution**: Area chart showing rating distribution
- **Install Tiers**: Horizontal bar chart showing install distribution
- **Category Analysis Table**: Detailed breakdown by category

### Insights
- Market dominance analysis
- Monetization trends
- User engagement patterns

## 🚀 Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## 🔧 Configuration

### API Proxy
The Vite config includes a proxy to forward API requests to the backend:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true
  }
}
```

### Tailwind CSS
Custom colors and fonts are configured in `tailwind.config.js` to match the Google Play Store theme.

## 📱 Responsive Design

The frontend is fully responsive with breakpoints for:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## 🎯 Usage

1. **Homepage**: Visit the root URL to see the landing page with feature overview
2. **Dashboard**: Click "Explore Dashboard" or navigate to `/dashboard` to view analytics
3. **Refresh**: Use the refresh button in the dashboard to fetch latest data

## 🐛 Troubleshooting

### API Connection Issues
- Ensure the Flask backend is running on `http://localhost:5000`
- Check that CORS is enabled on the backend
- Verify the API endpoints are accessible

### Styling Issues
- Make sure Tailwind CSS dependencies are installed
- Check that `postcss.config.js` and `tailwind.config.js` are properly configured
- Clear browser cache if styles don't update

### Build Issues
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Ensure Node.js version is 16 or higher

## 📝 License

This is a university project for Mobile App Market Analysis.

## 👥 Team

University Fourth Year Project | 2026
