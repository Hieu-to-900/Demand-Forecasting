import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

function SupplyChain({ forecastData }) {
  const inventoryMetrics = useMemo(() => {
    if (!forecastData?.supply_chain_optimization) {
      return null;
    }

    const sc = forecastData.supply_chain_optimization;
    return {
      currentStock: sc.inventory_parameters?.current_stock || 'N/A',
      reorderPoint: sc.inventory_parameters?.reorder_point || 'N/A',
      safetyStock: sc.inventory_parameters?.safety_stock || 'N/A',
      optimalOrderQuantity: sc.inventory_parameters?.optimal_order_quantity || 'N/A',
    };
  }, [forecastData]);

  const costData = useMemo(() => {
    if (!forecastData?.supply_chain_optimization?.cost_analysis) {
      return [];
    }

    const costs = forecastData.supply_chain_optimization.cost_analysis;
    return [
      { name: 'Holding Cost', value: costs.annual_holding_cost || 0 },
      { name: 'Ordering Cost', value: costs.annual_ordering_cost || 0 },
      { name: 'Total Cost', value: costs.total_annual_cost || 0 },
    ];
  }, [forecastData]);

  const recommendations = useMemo(() => {
    if (!forecastData?.supply_chain_optimization?.recommendations) {
      return [];
    }

    return forecastData.supply_chain_optimization.recommendations;
  }, [forecastData]);

  const needsReorder = useMemo(() => {
    if (!inventoryMetrics || inventoryMetrics.currentStock === 'N/A') {
      return false;
    }

    const current = parseFloat(inventoryMetrics.currentStock);
    const reorder = parseFloat(inventoryMetrics.reorderPoint);
    return current <= reorder;
  }, [inventoryMetrics]);

  if (!forecastData) {
    return <div className="dashboard-section">No data available</div>;
  }

  return (
    <div className="dashboard-section">
      <h2>Supply Chain Optimization</h2>

      <div className="metrics-cards">
        <div className="metric-card">
          <div className="metric-label">Current Stock</div>
          <div className="metric-value">{inventoryMetrics?.currentStock || 'N/A'}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Reorder Point</div>
          <div className="metric-value">{inventoryMetrics?.reorderPoint || 'N/A'}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Safety Stock</div>
          <div className="metric-value">{inventoryMetrics?.safetyStock || 'N/A'}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Optimal Order Qty</div>
          <div className="metric-value">{inventoryMetrics?.optimalOrderQuantity || 'N/A'}</div>
        </div>
      </div>

      {needsReorder && (
        <div className="alert-card alert-warning">
          <h3>⚠️ Reorder Alert</h3>
          <p>Current stock is at or below reorder point. Consider placing an order.</p>
        </div>
      )}

      <div className="chart-container">
        <h3>Cost Analysis</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={costData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
            <Legend />
            <Bar dataKey="value" fill="#667eea" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="recommendations-section">
        <h3>Reorder Recommendations</h3>
        <ul className="recommendations-list">
          {recommendations.map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default SupplyChain;

