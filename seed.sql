-- EV Charging Station Locator Database Schema
-- Run this SQL in Supabase SQL Editor

-- Drop existing tables if they exist (in correct order due to FK constraints)
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS stations;

-- Create stations table
CREATE TABLE stations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    connector_type TEXT NOT NULL,
    price_per_unit FLOAT NOT NULL,
    total_slots INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create bookings table
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    station_id INT NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    user_name TEXT NOT NULL,
    booking_time TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create indexes for faster queries
CREATE INDEX idx_stations_connector ON stations(connector_type);
CREATE INDEX idx_bookings_station ON bookings(station_id);

-- Enable Row Level Security (RLS)
ALTER TABLE stations ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Create policies to allow public access (for demo purposes)
CREATE POLICY "Allow public read access on stations" ON stations
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access on bookings" ON bookings
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert on bookings" ON bookings
    FOR INSERT WITH CHECK (true);

-- Insert 15 dummy EV charging stations in Pune with different connector types
INSERT INTO stations (name, latitude, longitude, connector_type, price_per_unit, total_slots) VALUES
    ('Tata Power EV Station - Koregaon Park', 18.5362, 73.8937, 'CCS', 12.50, 4),
    ('Ather Grid - Baner', 18.5590, 73.7868, 'Type2', 10.00, 6),
    ('Tesla Supercharger - Hinjewadi', 18.5912, 73.7380, 'Tesla', 15.00, 8),
    ('ChargeZone - Kharadi', 18.5514, 73.9403, 'CCS', 11.00, 5),
    ('Fortum Charge - Viman Nagar', 18.5679, 73.9143, 'Type2', 9.50, 3),
    ('EVSE India - Shivaji Nagar', 18.5308, 73.8475, 'CCS', 13.00, 4),
    ('Tesla Destination - Phoenix Mall', 18.5620, 73.9150, 'Tesla', 14.50, 6),
    ('Tata Power - Magarpatta City', 18.5180, 73.9270, 'Type2', 11.50, 5),
    ('ChargeGrid - Aundh', 18.5580, 73.8070, 'CCS', 12.00, 4),
    ('Ather Grid - Wakad', 18.5990, 73.7620, 'Type2', 10.50, 8),
    ('EV Motors - Hadapsar', 18.5020, 73.9430, 'CCS', 11.00, 3),
    ('Tesla Supercharger - Senapati Bapat Road', 18.5250, 73.8350, 'Tesla', 16.00, 10),
    ('Statiq - Camp Area', 18.5150, 73.8800, 'Type2', 9.00, 4),
    ('Kazam EV - Pimpri Chinchwad', 18.6280, 73.8000, 'CCS', 10.50, 6),
    ('Jio-BP Pulse - Swargate', 18.5010, 73.8580, 'Type2', 11.00, 5);

-- Verify the data
SELECT * FROM stations;
