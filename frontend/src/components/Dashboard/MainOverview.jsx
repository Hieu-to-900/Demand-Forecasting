import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import './Dashboard.css';

function MainOverview({ forecastData }) {
  const chartData = useMemo(() => {
    if (!forecastData?.historical_data || !forecastData?.seasonal_forecast) {
      return [];
    }

    const historical = forecastData.historical_data.map((item) => ({
      date: new Date(item.date).toLocaleDateString(),
      sales: item.sales,
      type: 'Historical',
      promotion: item.promotion === 1,
    }));

    const forecast = forecastData.seasonal_forecast.forecast_dates?.map((date, idx) => ({
      date: new Date(date).toLocaleDateString(),
      sales: forecastData.seasonal_forecast.forecast_values[idx],
      upper: forecastData.seasonal_forecast.forecast_upper?.[idx],
      lower: forecastData.seasonal_forecast.forecast_lower?.[idx],
      type: 'Forecast',
    })) || [];

    const lastHistoricalDate = historical[historical.length - 1]?.date;
    return [...historical, ...forecast].map((item) => ({
      ...item,
      isForecast: item.date >= lastHistoricalDate,
    }));
  }, [forecastData]);

  const metrics = useMemo(() => {
    if (!forecastData?.historical_data) {
      return null;
    }

    const historical = forecastData.historical_data;
    const totalSales = historical.reduce((sum, item) => sum + item.sales, 0);
    const avgDailyDemand = totalSales / historical.length;
    const growthRate = historical.length > 1
      ? ((historical[historical.length - 1].sales - historical[0].sales) / historical[0].sales) * 100
      : 0;

    const currentStock = forecastData.supply_chain_optimization?.inventory_parameters?.current_stock || 'N/A';
    const reorderPoint = forecastData.supply_chain_optimization?.inventory_parameters?.reorder_point || 'N/A';

    return {
      totalSales: totalSales.toFixed(0),
      avgDailyDemand: avgDailyDemand.toFixed(2),
      growthRate: growthRate.toFixed(2),
      currentStock,
      reorderPoint,
    };
  }, [forecastData]);

  if (!forecastData) {
    return <div className="dashboard-section">No data available</div>;
  }

  return (
    <div className="dashboard-section">
      <h2>Main Overview</h2>

      <div className="metrics-cards">
        <div className="metric-card">
          <div className="metric-label">Total Sales</div>
          <div className="metric-value">{metrics?.totalSales || 'N/A'}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Avg Daily Demand</div>
          <div className="metric-value">{metrics?.avgDailyDemand || 'N/A'}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Growth Rate</div>
          <div className="metric-value">{metrics?.growthRate || 'N/A'}%</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Current Stock</div>
          <div className="metric-value">{metrics?.currentStock}</div>
        </div>
      </div>

      <div className="chart-container">
        <h3>Historical Sales & Forecast</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Legend />
            <ReferenceLine
              x={chartData.find((d) => d.isForecast)?.date}
              stroke="#999"
              strokeDasharray="3 3"
              label="Forecast Start"
            />
            <Line
              type="monotone"
              dataKey="sales"
              stroke="#667eea"
              strokeWidth={2}
              dot={false}
              name="Sales"
            />
            {chartData.some((d) => d.upper) && (
              <>
                <Line
                  type="monotone"
                  dataKey="upper"
                  stroke="#82ca9d"
                  strokeDasharray="5 5"
                  dot={false}
                  name="Upper Bound"
                />
                <Line
                  type="monotone"
                  dataKey="lower"
                  stroke="#82ca9d"
                  strokeDasharray="5 5"
                  dot={false}
                  name="Lower Bound"
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default MainOverview;

