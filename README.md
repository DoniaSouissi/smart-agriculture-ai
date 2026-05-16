# 🌿 Smart Agriculture: Crop Health AI

An enterprise-grade, full-stack artificial intelligence application designed for high-precision foliar disease tracking and localized crop health assessment. Driven by optimized computer vision models (**YOLOv11 Object Detection & Instance Segmentation**), decoupled from a high-throughput **FastAPI** microservice backend, and presented via an interactive, meticulously styled **Streamlit** "Botanical Field Journal" frontend interface.

---

## 📑 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Key Features](#-key-features)
3. [Deep Learning Engine & Notebooks](#-deep-learning-engine--notebooks)
4. [Data Architecture & Class Mapping Shift](#-data-architecture--class-mapping-shift)
5. [Installation & Local Setup](#-installation--local-setup)
6. [API Service Configuration & Endpoints](#-api-service-configuration--endpoints)
7. [Frontend Client Design](#-frontend-client-design)
8. [Production Best Practices & Model Defense](#-production-best-practices--model-defense)
9. [License](#-license)

---

## 🏗 System Architecture
The ecosystem utilizes a decoupled, three-tier architecture engineered for modularity, low-latency execution, and zero-downtime model swap-outs.

| Step | From | To | Description |
|------|------|----|-------------|
| 1 | Streamlit UI | FastAPI Microservice | Uploads image (HTTP POST) |
| 2 | FastAPI Microservice | Lifespan Manager | Initialization |
| 3 | Lifespan Manager | YOLOv11s Detect | Load weights |
| 4 | Lifespan Manager | YOLOv11s Segment | Load weights |
| 5 | YOLOv11s Detect & Segment | FastAPI Microservice | Inference results |
| 6 | FastAPI Microservice | Streamlit UI | JPEG + X-Predictions |

**Layers:**
- **Client Layer** — Streamlit UI
- **API Middleware Layer** — FastAPI Microservice + Lifespan Manager
- **Deep Learning Layer** — YOLOv11s Detect, YOLOv11s Segment

* **Model Layer (Edge/Inference PyTorch):** Houses fine-tuned YOLOv11s object detection and instance segmentation models.
* **Inference Pipeline Middle-Tier (FastAPI):** Exposes endpoints via an asynchronous web framework, managing single-instantiation model lifecycles to maintain standard RAM footprints.
* **Presentation Workspace (Streamlit):** Serves as an interactive interface leveraging customized CSS layouts to maximize readability and enhance presentations.

---

## ✨ Key Features

* **Dual-Engine Analytics Execution:** Dynamically switch between standard rectangular bounding boxes (**Object Detection**) and tight, boundary-perfect polygon overlays (**Instance Segmentation**).
* **Decoupled Multi-Class Mapping & Binary Normalization:** The neural network maps 13 agricultural classes natively, while the API translates anomalies into an optimized **Healthy vs. Affected** binary status. This provides robust protection against long-tail dataset imbalances and guarantees clean UI notifications.
* **Real-time Confidence Filtering:** Interactive runtime thresholds allow fieldsmen to filter out low-probability false alerts instantly.
* **High-Performance Asynchronous Media Transfer:** Bypasses sluggish raw disk operations by processing uploads directly in-memory via `bytes/io` streams.
* **Unified Metadata Injector Architecture:** Transmits heavy annotated image arrays as direct `StreamingResponse` objects while embedding structured bounding-box and polygon arrays within serialized `X-Predictions` HTTP response headers.

---

## 🧠 Deep Learning Engine & Notebooks

The core modeling pipeline is fully documented and structured within two comprehensive Jupyter notebooks:

### 1. Object Detection (`objectdetection.ipynb`)
* **Network Baseline:** Pretrained COCO weights utilized via transfer learning (`yolo11s.pt`).
* **Hardware Acceleration:** Tailored for NVIDIA Tesla T4 GPUs with active optimizations for CUDA-based multi-threaded matrix operations.
* **Training Arguments:** Enhanced using Stochastic Gradient Descent variations (`AdamW` optimizer, initial learning rate `lr0=0.001`, batch sizing restricted tightly to `16` to prevent T4 memory overflows).
* **Augmentation Strategy:** Employs advanced spatial and color transformations including `mosaic=1.0` (swapped down automatically in the final 10 epochs using `close_mosaic=10` to lock validation stability), horizontal mirroring (`fliplr=0.5`), and spatial alpha blending (`mixup=0.1`).
* **Imbalance Overrides:** Regularized with structural class loss scaling (`cls=2.5`) and uniform noise distribution adjustments (`label_smoothing=0.1`) to suppress majority-class structural dominance.

### 2. Instance Segmentation (`segmentation.ipynb`)
* **Task Definition:** Precise spatial boundary delineation trained against complex contours.
* **Inference Formats:** Configured to compile both pixel-wise localization maps and raw floating-point spatial matrix polygons (`masks.xy`).

---

## 📊 Data Architecture & Class Mapping Shift

During dataset rebuilding and Roboflow generation updates, the system handles a standard sorting variation called **Class Mapping Shift**. To prevent index mismatch faults between the native numerical indices and string alphabetic organizations, the system leverages an updated dictionary configuration.

### Production Mapping Reference Matrix

| Class ID | Alphabetical Internal String Class | Production API Structural Translation | Target Pathology Classification |
| :---: | :---: | :---: | :--- |
| **0** | `0` | **Affected** | Bacterial Blight |
| **1** | `1` | **Affected** | Curl Virus |
| **2** | `10` | **Healthy** | **Healthy Specimen** |
| **3** | `11` | **Affected** | Septoria Leaf Spot |
| **4** | `12` | **Affected** | Yellow Leaf Curl |
| **5** | `2` | **Affected** | Herbicide Injury |
| **6** | `3` | **Affected** | Leaf Crinkle |
| **7** | `4` | **Affected** | Leaf Curl |
| **8** | `5` | **Affected** | Leaf Spot |
| **9** | `6` | **Affected** | Mosaic Virus |
| **10** | `7` | **Affected** | Powdery Mildew |
| **11** | `8` | **Affected** | Sudden Death |
| **12** | `9` | **Affected** | Target Spot |

---

## 🛠 Installation & Local Setup

### Prerequisite Environment
* Python 3.10 to 3.12 (64-bit Edition)
* CUDA Toolkit compatible drivers (Optional, for GPU-accelerated local execution)

### 1. Clone & Organize Project Workspace
```bash
git clone <repository-url> smart_agriculture_project
cd smart_agriculture_project
