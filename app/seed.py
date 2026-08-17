"""
Database initialization and comprehensive mock corpus seed script.
"""
import os
import json
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import User, Supervisor, Project, Submission, PlagiarismReport, SimilarityMatch, Feedback, Notification, AuditLog, SystemSetting
from app.core.security import get_password_hash
from app.core.config import settings
from app.services.plagiarism.engine import PlagiarismEngine

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables initialized successfully.")

def seed_data():
    """Seed initial demo accounts, settings, projects, documents, and notifications."""
    db: Session = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@example.com").first():
            print("Database already contains seed data. Skipping re-seed.")
            return

        print("Seeding system configuration settings...")
        default_settings = [
            ("institution_name", "Federal University of Science & Technology", "Name of the academic institution"),
            ("academic_year_current", "2025/2026", "Current active academic session"),
            ("max_file_size_mb", "25", "Maximum document upload size in megabytes"),
            ("similarity_threshold_warning", "40.0", "Similarity score above which a submission is flagged for review"),
            ("similarity_threshold_critical", "60.0", "Similarity score classified as high potential plagiarism"),
            ("allowed_file_types", ".pdf,.docx,.doc,.txt", "Comma-separated allowed document upload formats"),
            ("enable_automatic_plagiarism_check", "true", "Automatically compute similarity report upon document upload")
        ]
        for key, val, desc in default_settings:
            db.add(SystemSetting(key=key, value=val, description=desc))
        db.commit()

        print("Seeding users and supervisors...")
        # 1. Admin Account
        admin_user = User(
            full_name="System Administrator",
            email="admin@example.com",
            password_hash=get_password_hash("Admin@12345"),
            role="admin",
            department="Academic Registry",
            phone="+2348011223344",
            is_active=True
        )
        db.add(admin_user)

        # 2. Supervisor 1
        sup1_user = User(
            full_name="Prof. Ike Mgbeafulike",
            email="supervisor@example.com",
            password_hash=get_password_hash("Supervisor@12345"),
            role="supervisor",
            department="Computer Science",
            phone="+2348022334455",
            is_active=True
        )
        db.add(sup1_user)
        db.flush()

        sup1_profile = Supervisor(
            user_id=sup1_user.id,
            staff_id="STF/CSC/2014/082",
            department="Computer Science",
            specialization="Cybersecurity & Machine Learning",
            max_students=12
        )
        db.add(sup1_profile)

        # 3. Supervisor 2
        sup2_user = User(
            full_name="Dr. Sarah Alabi",
            email="sarah.alabi@example.com",
            password_hash=get_password_hash("Supervisor@12345"),
            role="supervisor",
            department="Software Engineering",
            phone="+2348033445566",
            is_active=True
        )
        db.add(sup2_user)
        db.flush()

        sup2_profile = Supervisor(
            user_id=sup2_user.id,
            staff_id="STF/SWE/2018/141",
            department="Software Engineering",
            specialization="Cloud Computing & Distributed Systems",
            max_students=10
        )
        db.add(sup2_profile)

        # 4. Student 1 (Demo Student)
        student1_user = User(
            full_name="Demo Student",
            email="student@example.com",
            password_hash=get_password_hash("Student@12345"),
            role="student",
            department="Computer Science",
            matric_number="CSC/2022/1042",
            phone="+2348044556677",
            is_active=True
        )
        db.add(student1_user)

        # 5. Student 2 (Chinedu Okafor)
        student2_user = User(
            full_name="Chinedu Okafor",
            email="chinedu@example.com",
            password_hash=get_password_hash("Student@12345"),
            role="student",
            department="Computer Science",
            matric_number="CSC/2022/1088",
            phone="+2348055667788",
            is_active=True
        )
        db.add(student2_user)

        # 6. Student 3 (Amina Bello)
        student3_user = User(
            full_name="Amina Bello",
            email="amina@example.com",
            password_hash=get_password_hash("Student@12345"),
            role="student",
            department="Software Engineering",
            matric_number="SWE/2022/2015",
            phone="+2348066778899",
            is_active=True
        )
        db.add(student3_user)

        db.commit()
        db.refresh(sup1_profile)
        db.refresh(sup2_profile)
        db.refresh(student1_user)
        db.refresh(student2_user)
        db.refresh(student3_user)

        print("Seeding projects and document submissions corpus...")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # Corpus Document 1: Historic research project by Chinedu
        corpus_text_1 = """
TITLE: Machine Learning Based Intrusion Detection System in Cloud Virtualized Environments

ABSTRACT:
Cloud computing infrastructures have become pivotal targets for sophisticated distributed cyber attacks. Traditional signature-based intrusion detection systems (IDS) struggle to classify polymorphic network traffic anomalies. This study presents a hybrid anomaly detection pipeline integrating Random Forest and Deep Autoencoders to inspect packet telemetry in software-defined network hypervisors. We evaluate the proposed model using the NSL-KDD and UNSW-NB15 benchmark datasets. Experimental results demonstrate that the hybrid approach attains an overall detection accuracy of 98.42% with a false positive rate reduced to 1.15%.

METHODOLOGY AND ARCHITECTURE:
Our preprocessing pipeline normalizes network flow durations, byte rates, and service flags using min-max feature scaling. Categorical attributes including protocol types and tcp connection flags are one-hot encoded. The feature selection phase applies mutual information gain to prune redundant dimensional vectors. The classification engine evaluates incoming packets in sliding temporal windows, comparing traffic entropy against learned baseline profiles.

EXPERIMENTAL RESULTS:
Across 10-fold cross validation, the ensemble model outperformed standard Support Vector Machines by 4.8% in precision. Confusion matrix analysis indicates rapid convergence within 45 training epochs. Computational latency benchmarks reveal an average packet evaluation overhead of 3.2 milliseconds, satisfying real-time line-rate monitoring constraints.
"""
        doc1_path = os.path.join(settings.UPLOAD_DIR, "seed_corpus_cloud_ids.txt")
        with open(doc1_path, "w", encoding="utf-8") as f:
            f.write(corpus_text_1.strip())

        proj1 = Project(
            title="Machine Learning Based Intrusion Detection System in Cloud Virtualized Environments",
            description="A hybrid anomaly detection framework combining Random Forest and Deep Autoencoders for packet telemetry inspection.",
            category="Cybersecurity",
            department="Computer Science",
            academic_session="2024/2025",
            student_id=student2_user.id,
            supervisor_id=sup1_profile.id,
            status="Approved"
        )
        db.add(proj1)
        db.flush()

        sub1 = Submission(
            project_id=proj1.id,
            version=1,
            original_filename="cloud_ids_final_thesis.txt",
            stored_filename="seed_corpus_cloud_ids.txt",
            file_path=doc1_path,
            file_type=".txt",
            file_size=len(corpus_text_1.encode("utf-8")),
            extracted_text=corpus_text_1.strip(),
            submitted_by=student2_user.id,
            submission_status="Approved"
        )
        db.add(sub1)
        db.commit()

        # Corpus Document 2: Blockchain paper by Amina
        corpus_text_2 = """
TITLE: Decentralized Electronic Health Record Architecture Using Zero-Knowledge Smart Contracts

ABSTRACT:
Interoperability and patient data sovereignty remain key bottlenecks in modern hospital information systems. This paper introduces MediGuard, an Ethereum-compatible distributed ledger framework that secures sensitive medical diagnostics while allowing privacy-preserving verification through zero-knowledge SNARK proofs. Patients maintain cryptographic ownership of encrypted medical files stored on IPFS, granting temporary granular access to accredited healthcare practitioners.

IMPLEMENTATION DETAILS:
Smart contracts written in Solidity v0.8.20 enforce access control policies, audit logging, and cryptographic signature validation. File payloads are symmetrically encrypted using AES-256-GCM before off-chain distribution. Gas consumption analysis confirms that batch authentication reduces operational transaction fees by 37.4%.

SECURITY AND PERFORMANCE ANALYSIS:
Formal verification of contract bytecodes was conducted via automated symbolic execution tools. The system withstood replay attacks, reentrancy vulnerabilities, and unauthorized privilege escalation. Storage throughput scaled linearly up to 500 concurrent patient record requests per second.
"""
        doc2_path = os.path.join(settings.UPLOAD_DIR, "seed_corpus_mediguard.txt")
        with open(doc2_path, "w", encoding="utf-8") as f:
            f.write(corpus_text_2.strip())

        proj2 = Project(
            title="Decentralized Electronic Health Record Architecture Using Zero-Knowledge Smart Contracts",
            description="Privacy-preserving electronic healthcare records management with Ethereum and IPFS.",
            category="Distributed Systems",
            department="Software Engineering",
            academic_session="2024/2025",
            student_id=student3_user.id,
            supervisor_id=sup2_profile.id,
            status="Approved"
        )
        db.add(proj2)
        db.flush()

        sub2 = Submission(
            project_id=proj2.id,
            version=1,
            original_filename="mediguard_ehr_paper.txt",
            stored_filename="seed_corpus_mediguard.txt",
            file_path=doc2_path,
            file_type=".txt",
            file_size=len(corpus_text_2.encode("utf-8")),
            extracted_text=corpus_text_2.strip(),
            submitted_by=student3_user.id,
            submission_status="Approved"
        )
        db.add(sub2)
        db.commit()

        # Student 1's Project A: High Similarity / Needs Review (Contains verbatim chunks from Document 1)
        demo_plagiarized_text = """
TITLE: Distributed Intrusion Detection Architecture for High-Speed Cloud Telemetry

ABSTRACT:
Cloud computing infrastructures have become pivotal targets for sophisticated distributed cyber attacks. Traditional signature-based intrusion detection systems struggle to classify polymorphic network traffic anomalies. In this research, we propose an intelligent threat detection pipeline for network hypervisors. We evaluate our methodology against the NSL-KDD and UNSW-NB15 benchmark datasets.

METHODOLOGY:
Our preprocessing pipeline normalizes network flow durations, byte rates, and service flags using min-max feature scaling. Categorical attributes including protocol types and tcp connection flags are one-hot encoded. The feature selection phase applies mutual information gain to prune redundant dimensional vectors. The classification engine evaluates incoming packets in sliding temporal windows, comparing traffic entropy against learned baseline profiles.

EXPERIMENTAL EVALUATION:
Across 10-fold cross validation, the ensemble model outperformed standard Support Vector Machines by 4.8% in precision. Computational latency benchmarks reveal an average packet evaluation overhead of 3.2 milliseconds, satisfying real-time line-rate monitoring constraints.
"""
        doc3_path = os.path.join(settings.UPLOAD_DIR, "demo_student_project_a.txt")
        with open(doc3_path, "w", encoding="utf-8") as f:
            f.write(demo_plagiarized_text.strip())

        proj3 = Project(
            title="Distributed Intrusion Detection Architecture for High-Speed Cloud Telemetry",
            description="Investigation into automated threat hunting and network telemetry analysis in cloud clusters.",
            category="Cybersecurity",
            department="Computer Science",
            academic_session="2025/2026",
            student_id=student1_user.id,
            supervisor_id=sup1_profile.id,
            status="Under Review"
        )
        db.add(proj3)
        db.flush()

        sub3 = Submission(
            project_id=proj3.id,
            version=1,
            original_filename="cloud_telemetry_intrusion_report_v1.txt",
            stored_filename="demo_student_project_a.txt",
            file_path=doc3_path,
            file_type=".txt",
            file_size=len(demo_plagiarized_text.encode("utf-8")),
            extracted_text=demo_plagiarized_text.strip(),
            submitted_by=student1_user.id,
            submission_status="Submitted"
        )
        db.add(sub3)
        db.commit()

        # Student 1's Project B: Original Research Project (Low Similarity)
        demo_original_text = """
TITLE: Automated Cassava Crop Disease Classification Using Lightweight Mobile Vision Transformers

ABSTRACT:
Early detection of foliar crop diseases is critical for safeguarding agricultural yields in Sub-Saharan Africa. Smallholder farmers often lack access to professional agronomists and high-end computational hardware. This project develops CassavaMobileViT, a compact vision transformer model optimized for edge inference on low-power mobile devices. Trained on a diverse field dataset of 15,000 leaf images representing five major cassava conditions (Cassava Mosaic Disease, Bacterial Blight, Brown Streak, Green Mottle, and Healthy), our architecture achieves 96.18% top-1 accuracy while occupying only 4.8 MB of memory footprint.

SYSTEM ARCHITECTURE AND EDGE OPTIMIZATION:
We employ depthwise separable convolutions combined with spatial self-attention blocks to maintain receptive field diversity without quadratic computational cost. Quantization-aware training (QAT) converts 32-bit floating point weights into int8 precision, yielding a 3.4x speedup on mobile neural processing units. The offline Progressive Web App delivers instant inference in less than 48 milliseconds without requiring an active internet connection.

FIELD VALIDATION AND FARMER FEEDBACK:
Pilot testing across 12 farming cooperatives in Oyo State demonstrated an 89% farmer satisfaction rate. Diagnostic precision was validated against laboratory PCR confirmations with high agreement.
"""
        doc4_path = os.path.join(settings.UPLOAD_DIR, "demo_student_project_b.txt")
        with open(doc4_path, "w", encoding="utf-8") as f:
            f.write(demo_original_text.strip())

        proj4 = Project(
            title="Automated Cassava Crop Disease Classification Using Lightweight Mobile Vision Transformers",
            description="Offline mobile edge vision transformer system assisting farmers in diagnosing crop foliar pathologies.",
            category="Machine Learning",
            department="Computer Science",
            academic_session="2025/2026",
            student_id=student1_user.id,
            supervisor_id=sup1_profile.id,
            status="Approved"
        )
        db.add(proj4)
        db.flush()

        sub4 = Submission(
            project_id=proj4.id,
            version=1,
            original_filename="cassava_vision_transformer_thesis.txt",
            stored_filename="demo_student_project_b.txt",
            file_path=doc4_path,
            file_type=".txt",
            file_size=len(demo_original_text.encode("utf-8")),
            extracted_text=demo_original_text.strip(),
            submitted_by=student1_user.id,
            submission_status="Approved"
        )
        db.add(sub4)
        db.commit()

        print("Executing plagiarism checks for initial submissions...")
        # Run plagiarism engine for all submissions
        rep1 = PlagiarismEngine.run_check(sub1.id, db=db, force_recheck=True)
        rep2 = PlagiarismEngine.run_check(sub2.id, db=db, force_recheck=True)
        rep3 = PlagiarismEngine.run_check(sub3.id, db=db, force_recheck=True) # Will match sub1
        rep4 = PlagiarismEngine.run_check(sub4.id, db=db, force_recheck=True) # Low similarity

        print(f"Generated Plagiarism Report for Project 3: {rep3.similarity_score}% ({rep3.result})")
        print(f"Generated Plagiarism Report for Project 4: {rep4.similarity_score}% ({rep4.result})")

        print("Seeding supervisor feedback and notifications...")
        # Feedback on Project 3
        fb1 = Feedback(
            project_id=proj3.id,
            supervisor_id=sup1_profile.id,
            feedback_text="Please review the methodology section. The similarity report indicates substantial text overlap with existing cloud IDS publications in our repository. Rewrite the literature review in your own original academic voice and submit revision 2.",
            status="Revision Required"
        )
        db.add(fb1)

        # Feedback on Project 4
        fb2 = Feedback(
            project_id=proj4.id,
            supervisor_id=sup1_profile.id,
            feedback_text="Outstanding originality and clear methodology on the MobileViT edge quantization. Approved for final defense presentation.",
            status="Approved"
        )
        db.add(fb2)

        # Audit logs
        audit_init = AuditLog(
            user_id=admin_user.id,
            action="SYSTEM_INIT",
            description="AcadGuard database initialized with standard academic departments, demo accounts, and research corpus."
        )
        db.add(audit_init)

        db.commit()
        print("Database seeded successfully with authentic academic records!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_data()
