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
  ScatterChart,
  Scatter,
} from 'recharts';
import './Dashboard.css';

function ForecastAnalysis({ forecastData }) {
  const seasonalData = useMemo(() => {
    if (!forecastData?.seasonal_forecast) {
      return [];
    }

    const forecast = forecastData.seasonal_forecast;
    return forecast.forecast_dates?.map((date, idx) => ({
      date: new Date(date).toLocaleDateString(),
      forecast: forecast.forecast_values[idx],
      upper: forecast.forecast_upper?.[idx],
      lower: forecast.forecast_lower?.[idx],
    })) || [];
  }, [forecastData]);

  const scenarioData = useMemo(() => {
    if (!forecastData?.scenario_planning?.scenarios) {
      return [];
    }

    const scenarios = forecastData.scenario_planning.scenarios;
    const dates = forecastData.scenario_planning.forecast_dates || [];

    return dates.map((date, idx) => ({
      date: new Date(date).toLocaleDateString(),
      optimistic: scenarios.optimistic?.forecast[idx],
      realistic: scenarios.realistic?.forecast[idx],
      pessimistic: scenarios.pessimistic?.forecast[idx],
      expected: forecastData.scenario_planning.expected_forecast[idx],
    }));
  }, [forecastData]);

  const anomalyData = useMemo(() => {
    if (!forecastData?.historical_data) {
      return [];
    }

    const anomalies = forecastData.pattern_analysis?.anomalies || [];
    const historical = forecastData.historical_data || [];

    return historical.map((item) => {
      const anomalyDate = new Date(item.date).toISOString().split('T')[0];
      const isAnomaly = anomalies.some((a) => {
        const aDate = new Date(a.date).toISOString().split('T')[0];
        return aDate === anomalyDate;
      });
      return {
        date: new Date(item.date).toLocaleDateString(),
        sales: item.sales,
        isAnomaly,
      };
    });
  }, [forecastData]);

  if (!forecastData) {
    return <div className="dashboard-section">No data available</div>;
  }

  return (
    <div className="dashboard-section">
      <h2>Forecast Analysis</h2>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Seasonal Forecast with Confidence Intervals</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={seasonalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#667eea"
                strokeWidth={2}
                name="Forecast"
              />
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
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Scenario Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scenarioData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="optimistic"
                stroke="#4caf50"
                strokeWidth={2}
                name="Optimistic"
              />
              <Line
                type="monotone"
                dataKey="realistic"
                stroke="#2196f3"
                strokeWidth={2}
                name="Realistic"
              />
              <Line
                type="monotone"
                dataKey="pessimistic"
                stroke="#f44336"
                strokeWidth={2}
                name="Pessimistic"
              />
              <Line
                type="monotone"
                dataKey="expected"
                stroke="#ff9800"
                strokeDasharray="5 5"
                strokeWidth={2}
                name="Expected Value"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Anomaly Detection</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={anomalyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="sales"
                stroke="#667eea"
                strokeWidth={2}
                name="Sales"
                dot={(props) => {
                  const { payload } = props;
                  return payload.isAnomaly ? (
                    <circle cx={props.cx} cy={props.cy} r={5} fill="#f44336" />
                  ) : (
                    <circle cx={props.cx} cy={props.cy} r={2} fill="#667eea" />
                  );
                }}
              />
            </LineChart>
          </ResponsiveContainer>
          {forecastData.pattern_analysis?.anomalies && (
            <div className="anomaly-list">
              <h4>Detected Anomalies:</h4>
              <ul>
                {forecastData.pattern_analysis.anomalies.slice(0, 5).map((anomaly, idx) => (
                  <li key={idx}>
                    {new Date(anomaly.date).toLocaleDateString()}: {anomaly.sales?.toFixed(2)} units
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ForecastAnalysis;

