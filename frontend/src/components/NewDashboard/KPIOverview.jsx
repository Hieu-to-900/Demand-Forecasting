import React from 'react';
import './KPIOverview.css';

const KPIOverview = ({ kpiData }) => {
  if (!kpiData || !Array.isArray(kpiData)) {
    console.error('[KPIOverview] Invalid kpiData:', kpiData);
    return <div>Loading KPIs...</div>;
  }

  const getStatusColor = (status) => {
    const colors = {
      'excellent': '#10b981',
      'good': '#3b82f6',
      'warning': '#f59e0b',
      'critical': '#ef4444'
    };
    return colors[status] || '#6b7280';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') return '↑';
    if (trend === 'down') return '↓';
    return '→';
  };

  const formatValue = (kpi) => {
    if (kpi.id === 'forecast_accuracy' || kpi.id === 'production_load') {
      return `${kpi.value}%`;
    }
    if (kpi.id === 'demand_change') {
      return `${kpi.value > 0 ? '+' : ''}${kpi.value}%`;
    }
    if (kpi.id === 'inventory_cover') {
      return `${kpi.value} ngày`;
    }
    if (kpi.id === 'stockout_risk') {
      return kpi.value;
    }
    return kpi.value;
  };

  const formatChange = (change, trend) => {
    if (typeof change === 'string') return change;
    const sign = change > 0 ? '+' : '';
    return `${sign}${change}%`;
  };

  return (
    <div className="kpi-overview">
      <div className="kpi-grid">
        {kpiData.map((kpi) => (
          <div key={kpi.id} className="kpi-card" style={{ borderLeftColor: getStatusColor(kpi.status) }}>
            <div className="kpi-header">
              <span className="kpi-icon">{kpi.icon}</span>
              <span className="kpi-title">{kpi.title}</span>
            </div>
            <div className="kpi-value">
              {formatValue(kpi)}
            </div>
            <div className="kpi-footer">
              <span className={`kpi-change ${kpi.trend}`}>
                <span className="trend-icon">{getTrendIcon(kpi.trend)}</span>
                {formatChange(kpi.change, kpi.trend)}
              </span>
              <span className="kpi-period">vs 30 ngày trước</span>
            </div>
            {kpi.id === 'stockout_risk' && (
              <div className="risk-bar">
                <div 
                  className="risk-fill" 
                  style={{ 
                    width: `${kpi.riskScore}%`, 
                    backgroundColor: getStatusColor(kpi.status) 
                  }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default KPIOverview;
