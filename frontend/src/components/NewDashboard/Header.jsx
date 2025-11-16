import React, { useState } from 'react';
import './Header.css';

function Header({ filters, onFilterChange, categories = [], regions = [] }) {
  const [notificationCount, setNotificationCount] = useState(7);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProductDropdown, setShowProductDropdown] = useState(false);
  const [showRegionDropdown, setShowRegionDropdown] = useState(false);

  const timeRanges = [
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
    { value: '6m', label: 'Last 6 Months' },
    { value: 'ytd', label: 'Year to Date' }
  ];

  return (
    <header className="dashboard-header">
      <div className="header-container">
        {/* Left: Logo & Title */}
        <div className="header-brand">
          <div className="logo-mark">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="6" fill="url(#gradient)"/>
              <path d="M8 14L12 18L20 10" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="28" y2="28">
                  <stop offset="0%" stopColor="#3b82f6"/>
                  <stop offset="100%" stopColor="#1e40af"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="brand-text">
            <h1 className="brand-title">DENSO Intelligence</h1>
            <p className="brand-subtitle">Demand Forecasting & Risk Analysis</p>
          </div>
        </div>

        {/* Center: Filters */}
        <div className="header-filters">
          {/* Time Range */}
          <div className="filter-item">
            <select
              value={filters.timeRange}
              onChange={(e) => onFilterChange({ timeRange: e.target.value })}
              className="filter-select minimal"
            >
              {timeRanges.map(range => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
          </div>

          {/* Product Category */}
          <div className="filter-item dropdown-container">
            <button
              className="filter-button"
              onClick={() => {
                setShowProductDropdown(!showProductDropdown);
                setShowRegionDropdown(false);
              }}
            >
              <span className="filter-label">
                {filters.products?.length > 0 
                  ? `${filters.products.length} Categories` 
                  : 'All Products'}
              </span>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="chevron">
                <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            {showProductDropdown && (
              <div className="dropdown-panel">
                <div className="dropdown-header">
                  <span className="dropdown-title">Product Categories</span>
                  {filters.products?.length > 0 && (
                    <button 
                      className="clear-button"
                      onClick={() => onFilterChange({ products: [] })}
                    >
                      Clear
                    </button>
                  )}
                </div>
                <div className="dropdown-content">
                  {categories.map(cat => (
                    <label key={cat.id} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={filters.products?.includes(cat.id)}
                        onChange={(e) => {
                          const newProducts = e.target.checked
                            ? [...(filters.products || []), cat.id]
                            : (filters.products || []).filter(p => p !== cat.id);
                          onFilterChange({ products: newProducts });
                        }}
                      />
                      <span className="checkbox-label">{cat.name}</span>
                      <span className="checkbox-count">{cat.count}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Market Region */}
          <div className="filter-item dropdown-container">
            <button
              className="filter-button"
              onClick={() => {
                setShowRegionDropdown(!showRegionDropdown);
                setShowProductDropdown(false);
              }}
            >
              <span className="filter-label">
                {filters.regions?.length > 0 
                  ? `${filters.regions.length} Regions` 
                  : 'All Regions'}
              </span>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="chevron">
                <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            {showRegionDropdown && (
              <div className="dropdown-panel">
                <div className="dropdown-header">
                  <span className="dropdown-title">Market Regions</span>
                  {filters.regions?.length > 0 && (
                    <button 
                      className="clear-button"
                      onClick={() => onFilterChange({ regions: [] })}
                    >
                      Clear
                    </button>
                  )}
                </div>
                <div className="dropdown-content">
                  {regions.map(region => (
                    <label key={region.id} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={filters.regions?.includes(region.id)}
                        onChange={(e) => {
                          const newRegions = e.target.checked
                            ? [...(filters.regions || []), region.id]
                            : (filters.regions || []).filter(r => r !== region.id);
                          onFilterChange({ regions: newRegions });
                        }}
                      />
                      <span className="checkbox-label">{region.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Search */}
          <div className="filter-item search-container">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="search-icon">
              <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M11 11L14 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <input
              type="text"
              placeholder="Search..."
              value={filters.searchQuery}
              onChange={(e) => onFilterChange({ searchQuery: e.target.value })}
              className="search-input"
            />
          </div>
        </div>

        {/* Right: Actions */}
        <div className="header-actions">
          <button className="action-button" title="Refresh">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M14.5 4.5C13.2 3.2 11.4 2.5 9.5 2.5C5.9 2.5 3 5.4 3 9C3 12.6 5.9 15.5 9.5 15.5C12.5 15.5 15 13.4 15.4 10.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M12 4.5H14.5V7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>

          <button 
            className="action-button notification-button" 
            onClick={() => setShowNotifications(!showNotifications)}
            title="Notifications"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M6.5 15.5C6.5 16.6 7.4 17.5 8.5 17.5C9.6 17.5 10.5 16.6 10.5 15.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M2.5 12.5H14.5V11.5C14.5 11.5 13.5 10.5 13.5 7.5C13.5 5.3 11.7 3.5 9.5 3.5H8.5C6.3 3.5 4.5 5.3 4.5 7.5C4.5 10.5 3.5 11.5 3.5 11.5V12.5H2.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {notificationCount > 0 && (
              <span className="notification-badge">{notificationCount}</span>
            )}
          </button>

          <div className="divider"></div>

          <div className="user-menu">
            <div className="user-avatar">
              <span>A</span>
            </div>
          </div>
        </div>
      </div>

      {/* Notification Panel */}
      {showNotifications && (
        <div className="notification-panel">
          <div className="panel-header">
            <h3>Notifications</h3>
            <button 
              className="clear-button"
              onClick={() => setNotificationCount(0)}
            >
              Mark all read
            </button>
          </div>
          <div className="panel-content">
            <div className="notification-item unread">
              <div className="notification-dot critical"></div>
              <div className="notification-body">
                <p className="notification-title">High Risk Alert: Port congestion</p>
                <p className="notification-desc">Yokohama delays affecting production</p>
                <span className="notification-time">5m ago</span>
              </div>
            </div>
            <div className="notification-item unread">
              <div className="notification-dot info"></div>
              <div className="notification-body">
                <p className="notification-title">Forecast Updated</p>
                <p className="notification-desc">Q2 demand spike predicted +18%</p>
                <span className="notification-time">1h ago</span>
              </div>
            </div>
            <div className="notification-item">
              <div className="notification-dot success"></div>
              <div className="notification-body">
                <p className="notification-title">Action Completed</p>
                <p className="notification-desc">Production schedule updated</p>
                <span className="notification-time">3h ago</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

export default Header;
