-- Create the stations table for EV Charging Station Locator
-- Run this in your Supabase SQL Editor

-- Drop table if exists (optional, for clean setup)
DROP TABLE IF EXISTS stations;

-- Create stations table
CREATE TABLE stations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    charger_type TEXT NOT NULL,
    price TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Enable Row Level Security (RLS) - optional but recommended
ALTER TABLE stations ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow public read access
CREATE POLICY "Allow public read access" ON stations
    FOR SELECT
    USING (true);

-- Insert 5 dummy EV stations around Pune, India
INSERT INTO stations (name, latitude, longitude, charger_type, price, status) VALUES
    ('Tata Power EV Station - Koregaon Park', 18.5362, 73.8939, 'DC Fast (50kW)', '₹15/kWh', 'Available'),
    ('EESL Charging Hub - Hinjewadi', 18.5912, 73.7380, 'CCS2 (150kW)', '₹18/kWh', 'Available'),
    ('Ather Grid - Viman Nagar', 18.5679, 73.9143, 'AC Slow (7.4kW)', '₹12/kWh', 'Busy'),
    ('ChargeZone - Shivaji Nagar', 18.5308, 73.8475, 'DC Fast (60kW)', '₹16/kWh', 'Available'),
    ('Fortum Charge - Baner', 18.5590, 73.7868, 'CCS2 + CHAdeMO (100kW)', '₹20/kWh', 'Maintenance');

-- Verify the data
SELECT * FROM stations;
