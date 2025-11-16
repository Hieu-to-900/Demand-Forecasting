import React, { useState, useEffect } from 'react';
import Header from './components/NewDashboard/Header';
import KPIOverview from './components/NewDashboard/KPIOverview';
import ForecastVisualization from './components/NewDashboard/ForecastVisualization';
import RiskIntelligence from './components/NewDashboard/RiskIntelligence';
import ActionRecommendations from './components/NewDashboard/ActionRecommendations';
import { mockData } from './data/mockData';
import './components/NewDashboard/NewDashboard.css';

function NewDashboard() {
  console.log('[NewDashboard] Component mounted');
  console.log('[NewDashboard] mockData:', mockData);

  const [filters, setFilters] = useState({
    timeRange: '90d',
    products: [],
    regions: [],
    searchQuery: ''
  });

  const [data, setData] = useState({
    kpis: mockData.kpis,
    forecast: mockData.forecast,
    newsRisks: mockData.newsRisks,
    actions: mockData.actions,
    regions: mockData.regions,
    categories: mockData.categories
  });

  console.log('[NewDashboard] Data state:', data);
  console.log('[NewDashboard] KPIs:', data.kpis);
  console.log('[NewDashboard] Forecast:', data.forecast);
  console.log('[NewDashboard] NewsRisks:', data.newsRisks);

  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
    // TODO: Fetch filtered data from backend
  };

  const handleActionUpdate = (actionId, status) => {
    setData(prevData => ({
      ...prevData,
      actions: prevData.actions.map(action =>
        action.id === actionId ? { ...action, status } : action
      )
    }));
  };

  console.log('[NewDashboard] Rendering...');

  return (
    <div className="new-dashboard">
      {/* HEADER - Global Control Center */}
      <Header
        filters={filters}
        onFilterChange={handleFilterChange}
        categories={data.categories}
        regions={data.regions}
      />

      <div className="dashboard-content">
        {/* TIER 1 - KPI Overview */}
        <section className="tier-1">
          <KPIOverview kpiData={data.kpis} />
        </section>

        {/* TIER 2 - Demand Forecasting Visualization */}
        <section className="tier-2">
          <ForecastVisualization forecastData={data.forecast} />
        </section>

        {/* TIER 3 - Risk & News Intelligence */}
        <section className="tier-3">
          <RiskIntelligence newsRisks={data.newsRisks} />
        </section>

        {/* TIER 4 - Action Recommendations */}
        <section className="tier-4">
          <ActionRecommendations
            actions={data.actions}
            onActionUpdate={handleActionUpdate}
          />
        </section>
      </div>
    </div>
  );
}

export default NewDashboard;
