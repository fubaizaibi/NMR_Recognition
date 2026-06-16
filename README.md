# NMR_Recognition
This project can initially achieve the recognition of simple nuclear magnetic resonance hydrogen spectra.
The Python package "NMR" in this directory is an AI-driven Nuclear Magnetic Resonance (NMR) spectrum intelligent identification system. It implements a complete closed-loop pipeline: "spectrum processing → peak detection → structure inference → report generation".

Below is an introduction to each module:

### 1. 'config.py' — Configuration Module
Stores global constants and default parameters, including random seed, noise threshold ratio, minimum peak distance, maximum candidate count, supported nuclei types (¹H, ¹³C), supported input file suffixes (CSV, JSON), and logger name. All business modules read from this centralized configuration.

### 2. 'logging_config.py' — Logging Configuration Module
Configures and returns a module-level logger with the format "timestamp | level | module | message". Provides a globally shared `LOGGER` instance.

### 3. 'models.py' — Data Model Module
Defines the core data structures:
- "SpectrumType" — Enum for spectrum types (¹H, ¹³C, HSQC, HMBC, COSY)
- "SpectrumPoint" — A single spectrum sampling point (chemical shift + intensity)
- "Peak" — Peak characteristics (shift, intensity, area, width, assignment, confidence)
- "Spectrum" — NMR spectrum data container
- "ParsedSpectrum" — Parsed spectrum result
- "MolecularCandidate" — Molecular structure candidate
- "AnalysisReport" — Final identification report

All dataclasses include field validation.

### 4. 'io.py' — Input/Output Module
- "SpectrumInputLoader" — Loads spectrum data from CSV or JSON files with automatic format detection
- "JsonReportWriter" — Serializes analysis reports to JSON files with proper Unicode encoding

### 5. 'processing.py' — Spectrum Signal Processing & Peak Detection Module
The core signal processing engine, implementing:
- Moving-average denoising
- Baseline correction
- Local-maximum peak detection
- Trapezoidal integration for peak area calculation
- Merging of closely-spaced peaks
- Spectrum quality score estimation

Includes a heuristic chemical shift region assignment function that identifies proton types (aliphatic, aromatic, aldehyde, etc.) based on ppm values.

### 6. 'prediction.py' — Theoretical Spectrum Prediction Module
The "HeuristicSpectrumPredictor" class maintains a built-in library of theoretical peak templates for common organic compounds (ethanol, acetone, toluene, ethyl acetate, benzaldehyde, phenol). It predicts ¹H NMR spectra by template lookup. In production, this can be replaced by GNN or Transformer deep learning models.

### 7. 'database.py' — Structure Database Module
The "StructureDatabase" class simulates a chemical knowledge graph with 6 built-in compound records (ethanol, acetone, toluene, ethyl acetate, benzaldehyde, phenol), including names, SMILES notations, molecular formulas, and compound classifications. A real system would connect to PubChem, MetaboLights, or enterprise databases.

### 8. 'inference.py' — Multimodal Structure Inference Engine Module
The "StructureInferenceEngine" integrates the structure database and theoretical spectrum predictor to perform reverse structure elucidation by matching observed peaks against theoretical peaks. The scoring algorithm considers both peak shift error and peak coverage, returning candidates sorted by score descending. Time complexity: O(c × n × m).

### 9. 'reasoning.py' — Expert Reasoning & Report Generation Module
The "ExpertReasoningEngine" simulates the logic of a spectroscopist, organizing peak features, structure candidates, and matching evidence into readable natural-language reasoning reports. It includes spectrum quality assessment, peak assignments, candidate rankings with evidence, and warning items.

### 10. 'system.py' — System Application Service Layer (Facade Class)
The "NmrAiIdentificationSystem" facade integrates the entire analysis pipeline — spectrum parsing → structure inference → report generation. It offers two convenience methods: `analyze_spectrum()` (direct spectrum input) and `analyze_file()` (file-based input with report export), hiding all internal module dependencies.

### 11. 'demo.py' — Demo & CLI Entry Point Module
- "DemoSpectrumFactory" — Generates realistic ¹H NMR demo spectra via Gaussian peak superposition with random noise
- "print_report_summary()" — Prints analysis report summary to console
- "main()" — Entry point for a one-click demo: generate sample spectrum → AI analysis → console output → JSON report export

### 12. '__init__.py' — Package Initialization Module
Exports all public APIs from the modules above, enabling convenient imports like `from NMR import NmrAiIdentificationSystem` without deep path traversal.
