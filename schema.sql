-- DESIGN DECISION COMMENTARY:
-- The hardest design decision was resolving guest identity across multiple channels (WhatsApp, Airbnb, direct email) 
-- to maintain "one record per guest". I opted for a 'guest_profiles' table (the master record) and a 
-- 'channel_identities' table. This allows a single guest to have multiple external IDs (a phone number for WhatsApp, 
-- a string ID for Airbnb) mapped to one master profile, preventing data duplication and fragmented conversation history.

-- 1. Master Guest Profile
CREATE TABLE guest_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    primary_email VARCHAR(255) UNIQUE,
    primary_phone VARCHAR(50) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Mapping different channel IDs (Booking.com, WhatsApp) to a single guest
CREATE TABLE channel_identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID REFERENCES guest_profiles(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL, -- e.g., 'whatsapp', 'airbnb'
    source_identifier VARCHAR(255) NOT NULL, -- The specific ID/number on that platform
    UNIQUE(source, source_identifier)
);

-- 2. Reservations
CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_ref VARCHAR(100) UNIQUE NOT NULL,
    guest_id UUID REFERENCES guest_profiles(id),
    property_id VARCHAR(100) NOT NULL,
    check_in_date DATE,
    check_out_date DATE,
    status VARCHAR(50) DEFAULT 'confirmed'
);

-- 3. Conversations (Linked to guests and reservations)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID REFERENCES guest_profiles(id),
    reservation_id UUID REFERENCES reservations(id) NULL,
    status VARCHAR(50) DEFAULT 'open', -- open, closed, snoozed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Messages (Unified table tracking AI states and metadata)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    message_text TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- AI and Routing Metadata
    query_type VARCHAR(100),
    ai_confidence_score DECIMAL(3, 2) CHECK (ai_confidence_score >= 0.0 AND ai_confidence_score <= 1.0),
    
    -- State Tracking
    is_ai_drafted BOOLEAN DEFAULT FALSE,
    is_agent_edited BOOLEAN DEFAULT FALSE,
    is_auto_sent BOOLEAN DEFAULT FALSE,
    
    -- Draft payload reference (what did the AI originally suggest before edits)
    original_ai_draft TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);