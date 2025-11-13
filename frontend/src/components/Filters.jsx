import { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import './Filters.css';

function Filters({ products, selectedProduct, onProductChange, filters, onFilterChange }) {
  const [localFilters, setLocalFilters] = useState(filters);

  const handleApply = () => {
    onFilterChange(localFilters);
  };

  const handleReset = () => {
    const defaultFilters = {
      forecastMode: 'comprehensive',
      forecastHorizonDays: 30,
      startDate: null,
      endDate: null,
    };
    setLocalFilters(defaultFilters);
    onFilterChange(defaultFilters);
  };

  return (
    <div className="filters-container">
      <div className="filters-card">
        <h3>Filters</h3>
        <div className="filters-grid">
          <div className="filter-item">
            <label>Product</label>
            <select
              value={selectedProduct}
              onChange={(e) => onProductChange(e.target.value)}
            >
              {products.map((product) => (
                <option key={product.product_id} value={product.product_id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-item">
            <label>Forecast Mode</label>
            <select
              value={localFilters.forecastMode}
              onChange={(e) =>
                setLocalFilters({ ...localFilters, forecastMode: e.target.value })
              }
            >
              <option value="comprehensive">Comprehensive</option>
              <option value="seasonal">Seasonal</option>
              <option value="promotional">Promotional</option>
              <option value="new_product">New Product</option>
            </select>
          </div>

          <div className="filter-item">
            <label>Forecast Horizon (days)</label>
            <input
              type="range"
              min="7"
              max="90"
              value={localFilters.forecastHorizonDays}
              onChange={(e) =>
                setLocalFilters({
                  ...localFilters,
                  forecastHorizonDays: parseInt(e.target.value),
                })
              }
            />
            <span>{localFilters.forecastHorizonDays} days</span>
          </div>

          <div className="filter-item">
            <label>Start Date</label>
            <DatePicker
              selected={localFilters.startDate}
              onChange={(date) =>
                setLocalFilters({ ...localFilters, startDate: date })
              }
              dateFormat="yyyy-MM-dd"
              isClearable
              placeholderText="Select start date"
            />
          </div>

          <div className="filter-item">
            <label>End Date</label>
            <DatePicker
              selected={localFilters.endDate}
              onChange={(date) =>
                setLocalFilters({ ...localFilters, endDate: date })
              }
              dateFormat="yyyy-MM-dd"
              isClearable
              placeholderText="Select end date"
              minDate={localFilters.startDate}
            />
          </div>
        </div>

        <div className="filter-actions">
          <button onClick={handleApply} className="btn-primary">
            Apply Filters
          </button>
          <button onClick={handleReset} className="btn-secondary">
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}

export default Filters;

