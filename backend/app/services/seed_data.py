from datetime import datetime
from pymongo.database import Database
from app.models.station import Station, RailwaySection, TrackAsset, StationMaintenanceHistory
from app.models.request import MaintenanceRequest
from app.models.plan import MaintenancePlan
from app.models.train import Train
from app.models.dispatch import DownstreamDispatch, ActivePossession
from app.models.audit import AuditLog, DataSource, DataImportLog
from app.database import init_indexes

def seed_database(db: Database):
    # Ensure indexes are established
    init_indexes(db)

    # Only seed if stations collection is empty
    if db["stations"].find_one():
        return

    # 1. STATIONS
    stations_data = [
        ("MAS", "Chennai Central", "SR", "Chennai Division", "KM 0.0 MAS", 13.0827, 80.2707, 42, "18 Sep 2026", "Engineering, TRD, S&T", "OPERATIONAL"),
        ("AJJ", "Arakkonam Junction", "SR", "Chennai Division", "KM 68.0 AJJ", 13.0805, 79.6698, 28, "20 Sep 2026", "Engineering, S&T", "OPERATIONAL"),
        ("SA", "Salem Junction", "SR", "Salem Division", "KM 334.0 SA", 11.6643, 78.1460, 35, "22 Sep 2026", "Engineering, TRD, S&T", "OPERATIONAL"),
        ("ED", "Erode Junction", "SR", "Salem Division", "KM 396.0 ED", 11.3410, 77.7172, 31, "19 Sep 2026", "Engineering, TRD", "OPERATIONAL"),
        ("TUP", "Tiruppur", "SR", "Salem Division", "KM 446.0 TUP", 11.1085, 77.3411, 19, "15 Sep 2026", "Engineering, TRD", "OPERATIONAL"),
        ("CBE", "Coimbatore Junction", "SR", "Salem Division", "KM 496.0 CBE", 11.0168, 76.9558, 38, "21 Sep 2026", "Engineering, TRD, S&T", "OPERATIONAL"),
        ("TPJ", "Tiruchchirappalli Junction", "SR", "Trichy Division", "KM 140.0 TPJ", 10.7905, 78.7047, 24, "17 Sep 2026", "Engineering, S&T", "OPERATIONAL"),
        ("MDU", "Madurai Junction", "SR", "Madurai Division", "KM 297.0 MDU", 9.9252, 78.1198, 22, "16 Sep 2026", "Engineering, TRD", "OPERATIONAL"),
    ]
    station_docs = [
        Station(
            station_code=code, station_name=name, zone=zone, division=div,
            location=loc, latitude=lat, longitude=lon, total_maintenance_works=works,
            last_maintenance_date=last_dt, departments_involved=depts, current_status=st
        ).to_dict()
        for code, name, zone, div, loc, lat, lon, works, last_dt, depts, st in stations_data
    ]
    db["stations"].insert_many(station_docs)

    # 2. RAILWAY SECTIONS
    sections_data = [
        ("SEC-MAS-AJJ", "Chennai - Arakkonam", "MAS", "AJJ", 0.0, 68.0, "QUAD LINE", 130, "YES (25KV AC)"),
        ("SEC-AJJ-SA", "Arakkonam - Salem", "AJJ", "SA", 68.0, 334.0, "DOUBLE LINE", 110, "YES (25KV AC)"),
        ("SEC-SA-ED", "Salem - Erode", "SA", "ED", 334.0, 396.0, "DOUBLE LINE", 110, "YES (25KV AC)"),
        ("SEC-ED-TUP", "Erode - Tiruppur", "ED", "TUP", 396.0, 446.0, "DOUBLE LINE", 110, "YES (25KV AC)"),
        ("SEC-TUP-CBE", "Tiruppur - Coimbatore", "TUP", "CBE", 446.0, 496.0, "DOUBLE LINE", 110, "YES (25KV AC)"),
        ("SEC-SA-TPJ", "Salem - Trichy", "SA", "TPJ", 0.0, 140.0, "SINGLE LINE", 100, "YES (25KV AC)"),
        ("SEC-TPJ-MDU", "Trichy - Madurai", "TPJ", "MDU", 0.0, 157.0, "DOUBLE LINE", 110, "YES (25KV AC)"),
    ]
    section_docs = [
        RailwaySection(
            section_id=s_id, section_name=name, from_station_code=f_code,
            to_station_code=t_code, km_start=km_s, km_end=km_e,
            line_type=l_type, max_speed_kmh=spd, electrified=elec
        ).to_dict()
        for s_id, name, f_code, t_code, km_s, km_e, l_type, spd, elec in sections_data
    ]
    db["railway_sections"].insert_many(section_docs)

    # 3. TRACK ASSETS
    assets_data = [
        ("TMS-001", "Engineering", "TMS", "Track", "Track Inspection (Ultrasonic USFD)", "KM 102/4 UP", "SA", "HIGH", "18 SEP 2026", "COMPLETED", "18 Sep 2026", "Good"),
        ("TMS-002", "Engineering", "TMS", "Track", "Thermit Weld Repair & Destressing", "KM 98/7 DN", "SA", "CRITICAL", "20 SEP 2026", "OVERDUE", "10 Aug 2026", "Requires Weld Grinding"),
        ("SMMS-004", "S&T", "SMMS", "Signal", "Track Circuit Shunting Sensitivity Test", "PODANUR YARD", "CBE", "HIGH", "22 SEP 2026", "REQUESTED", "15 Aug 2026", "Operational"),
        ("TDMS-003", "TRD", "TDMS", "OHE", "Contact Wire Height & Stagger Realignment", "KM 145/2", "ED", "MEDIUM", "25 SEP 2026", "UPCOMING", "01 Sep 2026", "Nominal"),
        ("TMS-005", "Engineering", "TMS", "Track", "Switch Expansion Joint (SEJ) Gap Reset", "KM 76/11", "SA", "CRITICAL", "21 SEP 2026", "OVERDUE", "05 Jul 2026", "Immediate Reset Mandatory"),
        ("TMS-006", "Engineering", "TMS", "Track", "Deep Screening Machine Ballast Cleaning", "KM 334/12 - 338/04", "SA", "HIGH", "26 SEP 2026", "REQUESTED", "12 May 2026", "High Fouling Index"),
        ("SMMS-007", "S&T", "SMMS", "Signal", "Axle Counter Interlock Point 42B Overhaul", "Point 42B SA", "SA", "CRITICAL", "26 SEP 2026", "OVERDUE", "18 Jul 2026", "G&SR-24 Restriction Active"),
    ]
    asset_docs = [
        TrackAsset(
            asset_id=a_id, department=dept, dept_ref=d_ref, asset_type=a_type,
            activity_description=desc, location=loc, station_code=st_code,
            priority=prio, schedule_date=sch, status=st,
            last_maintenance_date=last_m, condition_rating=cond
        ).to_dict()
        for a_id, dept, d_ref, a_type, desc, loc, st_code, prio, sch, st, last_m, cond in assets_data
    ]
    db["track_assets"].insert_many(asset_docs)

    # 4. MAINTENANCE REQUESTS
    reqs_data = [
        ("BR-2026-0142", "Engineering", "TMS", "SA", "SR", "Salem - Erode (KM 334/12 - 338/04)", "UP LINE", "TMS-006",
         "TRACK MAINTENANCE", "Deep screening machine and track destressing between Salem and Erode", "2026-09-26", "11:30", "13:00", 90, "HIGH", "High", "Tier-1",
         "Ultrasonic flaw testing indicated high localized rail stress", "SUBMITTED", "PENDING", "Clash with 3 scheduled passenger train movements"),
        
        ("BR-2026-0143", "S&T", "SMMS", "MAS", "SR", "Chennai - Arakkonam (UP LINE)", "UP LINE", "SMMS-007",
         "SIGNAL MAINTENANCE", "Interlock inspection and point motor renewal on UP trunk line", "2026-09-26", "14:00", "15:00", 60, "CRITICAL", "Immediate", "Tier-1",
         "Axle counter fault logged on Point 42B", "SUBMITTED", "CONFLICT DETECTED", "Directly overlaps scheduled run of Kovai Superfast Express (12691)"),
         
        ("BR-2026-0144", "TRD", "TDMS", "CBE", "SR", "Coimbatore - Tiruppur", "MAIN", "TDMS-003",
         "OHE 25KV MAINTENANCE", "OHE catenary contact wire replacement and tension verification", "2026-09-27", "09:30", "11:30", 120, "MEDIUM", "Standard", "Tier-2",
         "Routine 60-day contact wire wear cycle check", "SUBMITTED", "PENDING", "Evaluating morning goods freight slots"),
    ]
    req_docs = [
        MaintenanceRequest(
            request_id=r_id, department=dept, dept_ref=d_ref, station_code=s_code,
            zone=zone, segment=seg, track=trk, asset_id=a_id, maintenance_type=m_type,
            description=desc, requested_date=dt, requested_start_time=s_time,
            requested_end_time=e_time, duration_minutes=dur, priority=prio,
            urgency=urg, asset_criticality=crit, reason=rsn, status=st,
            conflict_flag=c_flg, conflict_summary=c_sum
        ).to_dict()
        for r_id, dept, d_ref, s_code, zone, seg, trk, a_id, m_type, desc, dt, s_time, e_time, dur, prio, urg, crit, rsn, st, c_flg, c_sum in reqs_data
    ]
    db["maintenance_requests"].insert_many(req_docs)

    # 5. PRE-GENERATED PLANS FOR BR-2026-0142
    plan_a = MaintenancePlan(
        plan_id="PLAN-BR-2026-0142-A",
        plan_code="PLAN A",
        request_id="BR-2026-0142",
        department="Engineering",
        station_code="SA",
        zone="SR",
        segment="Salem - Erode (KM 334/12 - 338/04)",
        track="UP LINE",
        maintenance_type="TRACK MAINTENANCE",
        requested_date="2026-09-26",
        requested_start_time="11:30",
        requested_end_time="13:00",
        recommended_date="2026-09-26",
        recommended_start_time="12:10",
        recommended_end_time="13:40",
        duration_minutes=90,
        priority="HIGH",
        risk_level="LOW",
        operational_impact="ACCEPTABLE SLA",
        reason_for_recommendation="Original request conflicts with 3 scheduled passenger train movements (TR 12675, TR 12691, TR 0942). Retiming by +40 minutes allows passing of Express 12691 before block inception, recovering freight flow via Salem loop line without cancellation.",
        conflicts_detected=0,
        delay_impact_min=18,
        resource_util_pct=84,
        recovered_trains=3,
        resource_gang="GANG #4 & TAMP",
        is_recommended=True,
        tier_resolution="TIER-1 RESOLUTION",
        status="SENT FOR APPROVAL"
    ).to_dict()

    plan_b = MaintenancePlan(
        plan_id="PLAN-BR-2026-0142-B",
        plan_code="PLAN B",
        request_id="BR-2026-0142",
        department="Engineering",
        station_code="SA",
        zone="SR",
        segment="Salem - Erode (KM 334/12 - 338/04)",
        track="UP LINE",
        maintenance_type="TRACK MAINTENANCE",
        requested_date="2026-09-26",
        requested_start_time="11:30",
        requested_end_time="13:00",
        recommended_date="2026-09-26",
        recommended_start_time="13:30",
        recommended_end_time="15:00",
        duration_minutes=90,
        priority="HIGH",
        risk_level="MEDIUM",
        operational_impact="MED IMPACT",
        reason_for_recommendation="Deferred slot into mid-afternoon off-peak corridor window. Minor hold-up of freight rake 0942 for 31 minutes at Salem North yard.",
        conflicts_detected=1,
        delay_impact_min=31,
        resource_util_pct=72,
        recovered_trains=2,
        resource_gang="GANG #4",
        is_recommended=False,
        tier_resolution="TIER-2 RESOLUTION",
        status="GENERATED"
    ).to_dict()

    plan_c = MaintenancePlan(
        plan_id="PLAN-BR-2026-0142-C",
        plan_code="PLAN C",
        request_id="BR-2026-0142",
        department="Engineering",
        station_code="SA",
        zone="SR",
        segment="Salem - Erode (KM 334/12 - 338/04)",
        track="UP LINE",
        maintenance_type="TRACK MAINTENANCE",
        requested_date="2026-09-26",
        requested_start_time="11:30",
        requested_end_time="13:00",
        recommended_date="2026-09-26",
        recommended_start_time="10:40",
        recommended_end_time="12:10",
        duration_minutes=90,
        priority="HIGH",
        risk_level="LOW",
        operational_impact="HIGH CREW LOAD",
        reason_for_recommendation="Advanced slot before Kovai Express departure. Requires early mobilization of Salem Section tamping machinery and permanent way gang.",
        conflicts_detected=0,
        delay_impact_min=24,
        resource_util_pct=91,
        recovered_trains=3,
        resource_gang="GANG #4 & CRANE",
        is_recommended=False,
        tier_resolution="TIER-2 RESOLUTION",
        status="GENERATED"
    ).to_dict()

    db["maintenance_plans"].insert_many([plan_a, plan_b, plan_c])

    # 6. DOWNSTREAM DISPATCHES
    dispatches = [
        ("BR-2026-0138", 1, "1. ENGINEERING DEPT", "SSE / Permanent Way (Salem)", "10:48:02", "SENT", None, None),
        ("BR-2026-0138", 2, "2. SIGNAL & TELECOM", "Section Controller (S&T)", "10:48:04", "SENT", None, None),
        ("BR-2026-0138", 3, "3. ELECTRICAL (OHE)", "Traction Power Controller (TPC)", "10:48:05", "SENT", None, None),
        ("BR-2026-0138", 4, "4. TRAFFIC CONTROL", "Chief Train Controller (CTC)", "10:48:06", "SENT", None, None),
        ("BR-2026-0138", 5, "5. DIVISION CONTROL", "DRM Operations Cell", "10:48:08", "SENT", None, None),
        ("BR-2026-0138", 6, "6. MAINTENANCE CREW", "Gang #4 Supervisor (Field Terminal)", "10:48:10", "ACKNOWLEDGED", "Gang #4 Supervisor", "10:48:12"),
    ]
    dispatch_docs = []
    for idx, (b_id, order, u_name, role, t_stamp, st, ack_by, ack_t) in enumerate(dispatches, start=1):
        d = DownstreamDispatch(
            block_id=b_id, unit_order=order, unit_name=u_name,
            recipient_role=role, sent_timestamp=t_stamp, status=st,
            acknowledged_by=ack_by, acknowledged_time=ack_t, id=idx
        ).to_dict()
        dispatch_docs.append(d)
    db["downstream_dispatches"].insert_many(dispatch_docs)
    db["counters"].update_one({"_id": "downstream_dispatches"}, {"$set": {"seq": len(dispatch_docs)}}, upsert=True)

    # 7. ACTIVE POSSESSION REGISTER
    possessions = [
        ("BR-2026-0138", "Chennai - Arakkonam", "SIGNAL", "10:00", "11:30", 2, "ACTIVE", "00:28:14", 5400, 3600, "Gang #1 (MAS)"),
        ("BR-2026-0140", "Salem - Erode", "ENGINEERING", "11:00", "13:00", 3, "ACTIVE", "01:05:32", 7200, 3300, "Gang #4 (Salem)"),
        ("BR-2026-0142", "Salem - Erode (MNT-3)", "ENGINEERING", "12:10", "13:40", 0, "ON SCHEDULE", "START IN 00:55", 5400, 0, "Gang #4 & TAMP"),
    ]
    possession_docs = [
        ActivePossession(
            block_id=b_id, section=sec, department=dept, start_time=st_t,
            end_time=e_t, trains_affected=tr_aff, status=st,
            remaining_display=rem, total_seconds_duration=tot_s,
            elapsed_seconds=el_s, resource_gang=gng
        ).to_dict()
        for b_id, sec, dept, st_t, e_t, tr_aff, st, rem, tot_s, el_s, gng in possessions
    ]
    db["active_possessions"].insert_many(possession_docs)

    # 8. TRAINS
    trains = [
        ("12675", "Kovai Superfast Express", "SUPERFAST EXPRESS", "MAS", "CBE", "South Corridor", 1, False),
        ("12691", "Nilgiri Express", "SUPERFAST EXPRESS", "MAS", "CBE", "South Corridor", 1, False),
        ("0942", "Container Freight Rake", "FREIGHT", "MAS", "ED", "South Corridor", 3, True),
    ]
    train_docs = [
        Train(
            train_number=num, train_name=name, train_type=t_type,
            origin=orig, destination=dest, corridor=corr, priority=prio,
            goods_train_indicator=goods
        ).to_dict()
        for num, name, t_type, orig, dest, corr, prio, goods in trains
    ]
    db["trains"].insert_many(train_docs)

    # 9. STATION MAINTENANCE HISTORY
    history_entries = [
        ("MNT-10482", "SA", "Salem Junction", "Engineering", "TMS-001", "Track 2", "Preventive Maintenance", "18 Sep 2026", 2026, "September", "18:00", "20:00", "2 hours", "Rail Joint RJ-204 maintenance and ultrasonic testing", "Completed", "Gang #4"),
        ("MNT-10481", "MAS", "Chennai Central", "S&T", "SMMS-004", "Platform 1", "Signal Inspection", "15 Sep 2026", 2026, "September", "01:00", "03:00", "2 hours", "Axle counter calibration and sensitivity renewal", "Completed", "S&T Team 1"),
        ("MNT-10480", "ED", "Erode Junction", "TRD", "TDMS-003", "Main Line", "OHE Inspection", "10 Sep 2026", 2026, "September", "02:00", "04:30", "2.5 hours", "25kV contact wire alignment and dropper adjustment", "Completed", "TRD Gang ED"),
        ("MNT-10479", "SA", "Salem Junction", "Engineering", "TMS-002", "Track 1", "Rail Joint Replacement", "04 Aug 2026", 2026, "August", "23:30", "02:30", "3 hours", "Thermit weld renewal and gap destressing at Point 18", "Completed", "Gang #4"),
        ("MNT-10478", "SA", "Salem Junction", "TRD", "TDMS-001", "Yard Line 2", "OHE Inspection", "12 Jun 2026", 2026, "June", "01:30", "03:30", "2 hours", "Traction feeder wire insulator cleaning", "Completed", "TRD Gang SA"),
        ("MNT-10477", "SA", "Salem Junction", "S&T", "SMMS-001", "Point 42B", "Signal Maintenance", "22 Mar 2026", 2026, "March", "10:00", "12:00", "2 hours", "Point machine drive rod replacement and test interlocking", "Completed", "S&T Unit SA"),
        ("MNT-10476", "SA", "Salem Junction", "Engineering", "TMS-003", "Main Line", "Track Inspection", "15 Jan 2026", 2026, "January", "09:00", "13:00", "4 hours", "Annual comprehensive track inspection and sleeper packing", "Completed", "Permanent Way Gang"),
        ("MNT-10475", "CBE", "Coimbatore Junction", "Engineering", "TMS-007", "Track 3", "Platform Maintenance", "05 Sep 2026", 2026, "September", "14:00", "17:00", "3 hours", "Track ballast renewal and edge clearance", "Completed", "Gang #2"),
        ("MNT-10474", "CBE", "Coimbatore Junction", "TRD", "TDMS-004", "Track 2", "Electrical Maintenance", "14 Aug 2026", 2026, "August", "00:00", "03:00", "3 hours", "Substation transformer relay testing", "Completed", "TRD Gang CBE"),
    ]
    history_docs = [
        StationMaintenanceHistory(
            maintenance_id=m_id, station_code=s_code, station_name=s_name,
            department=dept, asset_id=a_id, track=trk, maintenance_type=m_type,
            date=dt, year=yr, month=mo, start_time=s_time, end_time=e_time,
            duration_str=dur, description=desc, status=st, crew_gang=gng
        ).to_dict()
        for m_id, s_code, s_name, dept, a_id, trk, m_type, dt, yr, mo, s_time, e_time, dur, desc, st, gng in history_entries
    ]
    db["station_maintenance_history"].insert_many(history_docs)

    # 10. DATA SOURCES & AUDIT LOGS
    db["data_sources"].insert_many([
        DataSource(
            source_id="SRC-001",
            source_name="Indian Railways Southern Railway Master Corridor Register",
            source_type="CSV",
            file_name="sr_corridor_master_2026.csv",
            source_url="internal://cris/fois/sr_feed",
            description="Official Southern Railway sectional asset and chainage register"
        ).to_dict(),
        DataSource(
            source_id="SRC-002",
            source_name="Control Office Application (COA) Train Schedules",
            source_type="API",
            file_name="coa_live_schedules.json",
            source_url="https://fois.indianrail.gov.in/api/coa",
            description="Real-time train running and path allocation gateway"
        ).to_dict(),
    ])

    db["data_import_logs"].insert_many([
        DataImportLog(
            import_id="IMP-2026-001",
            filename="sr_track_assets.csv",
            source_type="CSV",
            total_rows=1420,
            successful_rows=1418,
            failed_rows=2,
            duplicate_rows=0,
            warnings=5,
            errors=0,
            status="Completed with warnings",
            notes="2 records flagged with non-standard chainage formatting; successfully mapped to default section"
        ).to_dict(),
        DataImportLog(
            import_id="IMP-2026-002",
            filename="coa_south_corridor_timings.json",
            source_type="JSON",
            total_rows=850,
            successful_rows=850,
            failed_rows=0,
            duplicate_rows=0,
            warnings=0,
            errors=0,
            status="Completed",
            notes="All scheduled paths ingested into train_schedules table with zero conflicts"
        ).to_dict(),
    ])

    db["audit_logs"].insert_one(
        AuditLog(
            id=1,
            user="R. Krishnan",
            role="PLANNER",
            action="System Initialized",
            entity_type="SYSTEM",
            entity_id="SYS-START",
            previous_status=None,
            new_status="ONLINE",
            comments="RailOps Southern Railway production cluster initialized on MongoDB Atlas"
        ).to_dict()
    )
    db["counters"].update_one({"_id": "audit_logs"}, {"$set": {"seq": 1}}, upsert=True)
