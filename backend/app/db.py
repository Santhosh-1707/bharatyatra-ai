import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bharatyatra.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enquiries (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        destination_id TEXT NOT NULL,
        destination_name TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        agency_name TEXT NOT NULL,
        traveler_name TEXT NOT NULL,
        traveler_phone TEXT NOT NULL,
        travel_dates TEXT,
        num_travelers INTEGER DEFAULT 2,
        notes TEXT,
        whatsapp_url TEXT,
        status TEXT DEFAULT 'New Lead'
    )
    """)
    conn.commit()
    conn.close()

def save_enquiry(record: Dict[str, Any]) -> Dict[str, Any]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    cursor.execute("""
    INSERT OR REPLACE INTO enquiries (
        id, created_at, destination_id, destination_name, agent_id,
        agent_name, agency_name, traveler_name, traveler_phone,
        travel_dates, num_travelers, notes, whatsapp_url, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["id"],
        created_at,
        record.get("destination_id", ""),
        record.get("destination_name", ""),
        record.get("agent_id", ""),
        record.get("agent_name", ""),
        record.get("agency_name", ""),
        record.get("traveler_name", ""),
        record.get("traveler_phone", ""),
        record.get("travel_dates", ""),
        record.get("num_travelers", 2),
        record.get("notes", ""),
        record.get("whatsapp_url", ""),
        record.get("status", "New Lead")
    ))
    conn.commit()
    conn.close()
    record["created_at"] = created_at
    return record

def get_all_enquiries() -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM enquiries ORDER BY created_at DESC")
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

def get_enquiries_count() -> int:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM enquiries")
    count = cursor.fetchone()[0]
    conn.close()
    return count
