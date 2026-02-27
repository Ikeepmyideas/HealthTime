-- =========================================================================
-- DATABASE SCHEMA : HealthTime (PostgreSQL)
-- =========================================================================

-- Création de la table des utilisateurs (Patients, Docteurs, Admins)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
    license_number VARCHAR(50) NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive'))
);

-- Création de la table des spécialités
CREATE TABLE IF NOT EXISTS specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Création de la table de liaison (Many-to-Many) Docteurs <-> Spécialités
CREATE TABLE IF NOT EXISTS doctor_specialties (
    doctor_id INT NOT NULL,
    specialty_id INT NOT NULL,
    PRIMARY KEY (doctor_id, specialty_id),
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (specialty_id) REFERENCES specialties(id) ON DELETE CASCADE
);

-- Création de la table des créneaux de disponibilité (Time Slots)
CREATE TABLE IF NOT EXISTS time_slots (
    id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL,
    slot_date DATE NOT NULL,
    slot_hour INT NOT NULL CHECK (slot_hour BETWEEN 0 AND 23),
    is_booked BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'booked', 'unavailable')),
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_doctor_slot UNIQUE (doctor_id, slot_date, slot_hour)
);

-- Création de la table des rendez-vous (Appointments)
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(30) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmé', 'completed', 'canceled', 'canceled_by_doctor', 'annulé')),
    urgent BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================================
-- INSERTION DES DONNÉES DE BASE
-- =========================================================================

-- Création du compte administrateur par défaut 
INSERT INTO users (name, username, password, role, status) 
VALUES ('Eren Jeager', 'eren', 'eren123', 'admin', 'active')
ON CONFLICT (username) DO NOTHING;

-- Ajout de toutes les spécialités médicales
INSERT INTO specialties (name) VALUES 
('Médecin généraliste'),
('Cardiologue'),
('Dermatologue'),
('Dentiste'),
('Gynécologue'),
('Pédiatre'),
('Ophtalmologue'),
('ORL'),
('Psychiatre'),
('Neurologue'),
('Urologue'),
('Orthopédiste'),
('Radiologue'),
('Chirurgien'),
('Anesthésiste'),
('Endocrinologue'),
('Gastro-entérologue'),
('Rhumatologue'),
('Allergologue'),
('Pneumologue'),
('Oncologue'),
('Néphrologue'),
('Médecine interne'),
('Médecine sportive')
ON CONFLICT (name) DO NOTHING;
