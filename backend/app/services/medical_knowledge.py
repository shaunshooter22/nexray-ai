# ============================================================
# NexRay AI - Medical Knowledge Base
# West African disease knowledge base for RAG system
# ============================================================

MEDICAL_DOCUMENTS = [
    {
        "id": "malaria_1",
        "content": """Disease: Malaria
Region: Ghana, West Africa
Causative Agent: Plasmodium falciparum (most common in West Africa), P. vivax, P. malariae
Symptoms: High fever (39-41°C), chills, rigors, sweating, headache, muscle aches, joint pain, fatigue, nausea, vomiting, anaemia, jaundice, splenomegaly. Fever is often cyclical (every 48-72 hours).
Severe Malaria Symptoms: Cerebral malaria (confusion, seizures, coma), severe anaemia, respiratory distress, hypoglycaemia, renal failure, pulmonary oedema.
Diagnosis: Malaria Rapid Diagnostic Test (RDT), blood smear microscopy, PCR.
Treatment: Artemisinin-based combination therapy (ACT) - artemether-lumefantrine (Coartem). Severe malaria: IV artesunate or quinine.
Urgency: Urgent to Emergency (especially in children and pregnant women).
Differential: Typhoid fever, dengue fever, viral haemorrhagic fever, pneumonia with fever."""
    },
    {
        "id": "typhoid_1",
        "content": """Disease: Typhoid Fever (Enteric Fever)
Region: Ghana, West Africa - common in areas with poor sanitation
Causative Agent: Salmonella typhi, Salmonella paratyphi
Symptoms: Sustained high fever (39-40°C) that rises gradually over 1 week, headache, abdominal pain, constipation or diarrhoea, rose spots on trunk (30% of cases), relative bradycardia, splenomegaly, hepatomegaly, malaise, anorexia.
Complications: Intestinal perforation, haemorrhage, myocarditis, encephalopathy.
Diagnosis: Blood culture (gold standard), Widal test, bone marrow culture, stool culture.
Treatment: Ciprofloxacin, ceftriaxone, azithromycin. Chloramphenicol (older option).
Urgency: Urgent.
Differential: Malaria, brucellosis, leptospirosis, viral hepatitis, tuberculosis."""
    },
    {
        "id": "pneumonia_1",
        "content": """Disease: Pneumonia
Region: Common across West Africa, major cause of mortality
Types: Community-acquired pneumonia (CAP), hospital-acquired pneumonia
Causative Agents: Streptococcus pneumoniae (most common), Haemophilus influenzae, Klebsiella pneumoniae, Mycoplasma pneumoniae, viral (influenza, COVID-19).
Symptoms: Productive cough with purulent sputum, high fever (38-40°C), chills, chest pain (pleuritic), shortness of breath, tachypnoea, tachycardia, reduced air entry on auscultation, dullness to percussion, bronchial breath sounds.
X-Ray Findings: Lobar consolidation, patchy infiltrates, air bronchograms, pleural effusion.
Diagnosis: Chest X-ray, sputum culture, blood culture, CBC (elevated WBC), CRP.
Treatment: Amoxicillin-clavulanate, azithromycin, ceftriaxone (severe). Oxygen therapy.
Urgency: Urgent to Emergency.
Differential: Tuberculosis, pulmonary oedema, lung cancer, pleural effusion."""
    },
    {
        "id": "tuberculosis_1",
        "content": """Disease: Tuberculosis (TB)
Region: Ghana, West Africa - high burden country
Causative Agent: Mycobacterium tuberculosis
Symptoms: Chronic productive cough (>2 weeks), blood-tinged sputum (haemoptysis), night sweats, weight loss, fever (low-grade, afternoon), fatigue, loss of appetite, chest pain, lymphadenopathy.
X-Ray Findings: Upper lobe infiltrates, cavitation, nodules, miliary pattern, hilar lymphadenopathy, pleural effusion.
Diagnosis: Sputum smear microscopy (AFB staining), GeneXpert/Xpert MTB/RIF, culture, chest X-ray, Mantoux test.
Treatment: HRZE regimen - Isoniazid, Rifampicin, Pyrazinamide, Ethambutol (2 months intensive + 4 months continuation).
Urgency: Urgent (public health concern - isolate patient).
Differential: Pneumonia, lung cancer, lymphoma, fungal infection, sarcoidosis."""
    },
    {
        "id": "dengue_1",
        "content": """Disease: Dengue Fever
Region: West Africa, increasing incidence in Ghana
Causative Agent: Dengue virus (DENV 1-4), transmitted by Aedes mosquito
Symptoms: Sudden high fever (39-40°C), severe headache, retro-orbital eye pain, severe joint and muscle pain (breakbone fever), skin rash (maculopapular, appears day 3-5), nausea, vomiting, mild bleeding (gum bleeding, epistaxis), fatigue.
Severe Dengue: Plasma leakage, haemorrhage, organ failure, dengue shock syndrome.
Diagnosis: NS1 antigen test (early), IgM/IgG serology, PCR. CBC: thrombocytopaenia (platelets <100,000), leucopaenia, elevated haematocrit.
Treatment: Supportive - IV fluids, paracetamol (avoid aspirin/NSAIDs), platelet transfusion if severe.
Urgency: Urgent to Emergency (severe dengue).
Differential: Malaria, typhoid, chikungunya, viral haemorrhagic fever."""
    },
    {
        "id": "meningitis_1",
        "content": """Disease: Bacterial Meningitis
Region: West Africa - meningitis belt includes northern Ghana
Causative Agents: Neisseria meningitidis (most common in Africa), Streptococcus pneumoniae, Haemophilus influenzae.
Symptoms: Severe headache, high fever, neck stiffness (meningismus), photophobia, phonophobia, altered consciousness, vomiting, seizures, purpuric rash (meningococcal).
Signs: Kernig's sign positive, Brudzinski's sign positive, papilloedema (raised ICP).
Diagnosis: Lumbar puncture (CSF analysis) - cloudy CSF, elevated protein, low glucose, neutrophilia. Blood culture, CT scan before LP if focal neurology.
Treatment: IV ceftriaxone or penicillin G. Dexamethasone (reduce inflammation).
Urgency: EMERGENCY - life threatening, treat immediately.
Differential: Viral meningitis, encephalitis, subarachnoid haemorrhage, cerebral malaria."""
    },
    {
        "id": "cholera_1",
        "content": """Disease: Cholera
Region: West Africa - endemic in coastal areas and during floods
Causative Agent: Vibrio cholerae O1 or O139
Symptoms: Sudden onset profuse watery diarrhoea (rice water stools), vomiting, rapid dehydration, muscle cramps, sunken eyes, dry mucous membranes, decreased skin turgor, hypotension, tachycardia. No fever typically.
Complications: Severe dehydration, electrolyte imbalance, hypovolaemic shock, renal failure, death if untreated.
Diagnosis: Stool culture, rapid cholera test strip, dark field microscopy.
Treatment: Oral rehydration salts (ORS) or IV fluids (Ringer's lactate). Antibiotics: doxycycline, azithromycin, ciprofloxacin. Zinc supplementation.
Urgency: Emergency (can kill within hours if dehydration severe).
Differential: Other causes of acute gastroenteritis, rotavirus, food poisoning, other diarrhoeal diseases."""
    },
    {
        "id": "sickle_cell_1",
        "content": """Disease: Sickle Cell Disease / Vaso-occlusive Crisis
Region: Very common in Ghana and West Africa (high carrier frequency)
Condition: Autosomal recessive haemoglobinopathy - HbSS
Symptoms of Crisis: Severe pain (bone, chest, abdomen, joints), fever, fatigue, pallor, jaundice (scleral icterus), shortness of breath, swollen hands/feet (dactylitis in children).
Acute Chest Syndrome: Fever, chest pain, hypoxia, new pulmonary infiltrate on X-ray.
Complications: Stroke, splenic sequestration, aplastic crisis, infections (especially encapsulated bacteria).
X-Ray: Cardiomegaly, pulmonary infiltrates (acute chest syndrome), bone changes.
Diagnosis: Haemoglobin electrophoresis, blood film (sickle cells), CBC (anaemia, reticulocytosis).
Treatment: Pain management (NSAIDs, opioids), IV fluids, oxygen, blood transfusion, hydroxyurea (chronic), exchange transfusion (severe).
Urgency: Urgent to Emergency.
Differential: Osteomyelitis, pneumonia, appendicitis, other causes of acute abdominal pain."""
    },
    {
        "id": "pleural_effusion_1",
        "content": """Condition: Pleural Effusion
Definition: Accumulation of fluid in the pleural space
Causes in West Africa: Tuberculosis (most common), pneumonia (parapneumonic), cardiac failure, malignancy, liver cirrhosis, nephrotic syndrome.
Symptoms: Dyspnoea, chest pain (pleuritic), dry cough, reduced breath sounds, dullness to percussion, tracheal deviation (large effusions).
X-Ray Findings: Blunting of costophrenic angle, homogeneous opacity (meniscus sign), mediastinal shift away from effusion (large).
Diagnosis: Chest X-ray, ultrasound, thoracocentesis (fluid analysis: LDH, protein, glucose, cytology, culture).
Treatment: Treat underlying cause. Thoracocentesis for large/symptomatic effusions. Chest drain for empyema.
Urgency: Urgent.
Differential: Consolidation, raised hemidiaphragm, subphrenic abscess."""
    },
    {
        "id": "heart_failure_1",
        "content": """Disease: Heart Failure / Cardiomegaly
Region: Common in West Africa - hypertensive heart disease, peripartum cardiomyopathy, rheumatic heart disease
Types: Left ventricular failure, right ventricular failure, biventricular failure
Symptoms: Dyspnoea (exertional then at rest), orthopnoea, paroxysmal nocturnal dyspnoea, ankle oedema, fatigue, reduced exercise tolerance, JVP elevation, S3 gallop.
X-Ray Findings: Cardiomegaly (CTR >0.5), pulmonary oedema (bat wing pattern, Kerley B lines), pleural effusion, upper lobe venous diversion.
Diagnosis: ECG, echocardiogram, BNP/NT-proBNP, chest X-ray, renal function.
Treatment: Diuretics (furosemide), ACE inhibitors/ARBs, beta-blockers, spironolactone. Treat underlying cause.
Urgency: Urgent to Emergency (acute pulmonary oedema).
Differential: COPD, pneumonia, pleural effusion."""
    },
    {
        "id": "appendicitis_1",
        "content": """Disease: Acute Appendicitis
Region: Common surgical emergency across West Africa
Symptoms: Pain starting around navel then migrating to right iliac fossa (McBurney's point), nausea, vomiting, fever (low-grade 37.5-38.5°C), anorexia, rebound tenderness, guarding, Rovsing's sign positive, psoas sign.
Complications: Perforation, peritonitis, abscess formation.
Diagnosis: Clinical (Alvarado score), CBC (leucocytosis with left shift), CRP elevated, ultrasound, CT scan.
Treatment: Surgical appendicectomy (open or laparoscopic). Antibiotics pre and post-op.
Urgency: Urgent to Emergency (perforated appendicitis = Emergency).
Differential: Ovarian cyst/torsion, ectopic pregnancy, mesenteric adenitis, Crohn's disease, pelvic inflammatory disease."""
    },
    {
        "id": "fracture_1",
        "content": """Condition: Bone Fracture
X-Ray Findings: Fracture line, cortical disruption, angulation, displacement, comminution, associated soft tissue swelling.
Types: Transverse, oblique, spiral, comminuted, greenstick (children), stress fracture, pathological fracture.
Common Sites: Distal radius (Colles), femoral neck (elderly), tibial shaft, vertebral compression.
Associated: Soft tissue injury, neurovascular compromise, open fracture (compound).
Diagnosis: X-ray (AP and lateral views), CT for complex fractures.
Treatment: Immobilisation (cast/splint), reduction (closed or open), surgical fixation (ORIF), physiotherapy.
Urgency: Urgent (open fractures and neurovascular compromise = Emergency).
Differential: Dislocation, soft tissue injury, bone cyst, osteosarcoma."""
    },
    {
        "id": "gastroenteritis_1",
        "content": """Disease: Acute Gastroenteritis
Region: Very common in West Africa - poor water sanitation
Causative Agents: Viral (rotavirus, norovirus), bacterial (E. coli, Salmonella, Shigella, Campylobacter), parasitic (Giardia, Entamoeba).
Symptoms: Nausea, vomiting, diarrhoea (watery or bloody), abdominal cramps, fever, dehydration (dry mouth, decreased urine output, sunken eyes in children).
Diagnosis: Stool culture (if bloody or prolonged), stool microscopy (ova and parasites).
Treatment: Oral rehydration salts, zinc supplementation (children), antibiotics only for specific bacterial causes (ciprofloxacin for Shigella, metronidazole for Giardia/Entamoeba).
Urgency: Routine to Urgent (depending on severity of dehydration).
Differential: Cholera, appendicitis, inflammatory bowel disease, food poisoning."""
    },
    {
        "id": "hypertension_1",
        "content": """Disease: Hypertensive Crisis / Severe Hypertension
Region: Very high prevalence in West Africa
Definition: BP >180/120 mmHg
Types: Hypertensive urgency (no end-organ damage), hypertensive emergency (with end-organ damage).
End-organ damage: Hypertensive encephalopathy, stroke, acute MI, aortic dissection, acute kidney injury, pulmonary oedema.
Symptoms: Headache, visual disturbance, chest pain, shortness of breath, confusion, seizures.
Diagnosis: BP measurement, ECG, renal function, urinalysis, fundoscopy (papilloedema), CT head.
Treatment: IV labetalol, nicardipine, hydralazine. Oral nifedipine (urgency). Reduce BP gradually.
Urgency: Emergency (hypertensive emergency with end-organ damage).
Differential: Phaeochromocytoma, pre-eclampsia, renal artery stenosis."""
    },
    {
        "id": "leptospirosis_1",
        "content": """Disease: Leptospirosis
Region: West Africa - common after flooding, contact with animals
Causative Agent: Leptospira interrogans
Symptoms: Biphasic illness. Phase 1 (leptospiraemic): fever, headache, myalgia, conjunctival suffusion. Phase 2 (immune): Weil's disease - jaundice, renal failure, haemorrhage, uveitis, meningitis.
Diagnosis: Serology (MAT - gold standard), PCR, urine culture (phase 2).
Treatment: Doxycycline (mild), penicillin/ceftriaxone (severe). Supportive care.
Urgency: Urgent to Emergency (Weil's disease).
Differential: Malaria, typhoid, viral hepatitis, dengue, meningitis."""
    },
]

# Symptom keyword mapping for quick retrieval
SYMPTOM_KEYWORD_MAP = {
    "fever": ["malaria_1", "typhoid_1", "dengue_1", "meningitis_1", "pneumonia_1", "leptospirosis_1"],
    "cough": ["pneumonia_1", "tuberculosis_1", "heart_failure_1"],
    "chest": ["pneumonia_1", "tuberculosis_1", "pleural_effusion_1", "heart_failure_1", "sickle_cell_1"],
    "headache": ["malaria_1", "meningitis_1", "dengue_1", "hypertension_1", "typhoid_1"],
    "diarrhoea": ["cholera_1", "gastroenteritis_1", "typhoid_1"],
    "diarrhea": ["cholera_1", "gastroenteritis_1", "typhoid_1"],
    "vomiting": ["cholera_1", "gastroenteritis_1", "malaria_1", "meningitis_1", "appendicitis_1"],
    "joint": ["malaria_1", "dengue_1", "sickle_cell_1"],
    "pain": ["sickle_cell_1", "appendicitis_1", "meningitis_1", "malaria_1"],
    "abdominal": ["typhoid_1", "appendicitis_1", "cholera_1", "gastroenteritis_1", "sickle_cell_1"],
    "neck": ["meningitis_1"],
    "stiff": ["meningitis_1"],
    "rash": ["dengue_1", "typhoid_1", "meningitis_1"],
    "breath": ["pneumonia_1", "heart_failure_1", "pleural_effusion_1", "sickle_cell_1"],
    "shortness": ["pneumonia_1", "heart_failure_1", "pleural_effusion_1"],
    "weight": ["tuberculosis_1"],
    "night": ["tuberculosis_1"],
    "sweat": ["tuberculosis_1", "malaria_1"],
    "jaundice": ["malaria_1", "leptospirosis_1", "sickle_cell_1"],
    "fracture": ["fracture_1"],
    "bone": ["fracture_1", "sickle_cell_1"],
    "swelling": ["heart_failure_1", "appendicitis_1"],
    "confusion": ["meningitis_1", "malaria_1", "hypertension_1"],
    "seizure": ["meningitis_1", "malaria_1", "hypertension_1"],
    "dehydration": ["cholera_1", "gastroenteritis_1"],
    "water": ["cholera_1"],
    "rice": ["cholera_1"],
    "sickle": ["sickle_cell_1"],
    "anaemia": ["sickle_cell_1", "malaria_1"],
    "anemia": ["sickle_cell_1", "malaria_1"],
    "blood": ["tuberculosis_1", "sickle_cell_1"],
    "pressure": ["hypertension_1"],
    "hypertension": ["hypertension_1", "heart_failure_1"],
    "chills": ["malaria_1", "pneumonia_1"],
    "rigors": ["malaria_1"],
    "eye": ["dengue_1", "meningitis_1"],
    "muscle": ["malaria_1", "dengue_1", "leptospirosis_1"],
    "fatigue": ["malaria_1", "tuberculosis_1", "dengue_1", "sickle_cell_1"],
    "appetite": ["tuberculosis_1", "typhoid_1", "malaria_1"],
}