# Balancing-Project

A processing pipeline for the Balance and Multimodal Communication Project.

## Prerequisites

Before getting started, ensure you have set up your virtual environment following the [pose2sim project](https://github.com/perfanalytics/pose2sim) requirements.

## Project Overview

[Brief description of what the project does and its main goals]

## Installation

1. Clone the repository:
```bash
git clone [[repository-url]](https://github.com/JH-Eric-Yang/Balancing-Project.git)
```

2. Set up the virtual environment (as per pose2sim requirements)

## Usage

1. Data Preparation
   - Create a `/Data` folder in the project root directory
   - Place your collected data folders into the `/Data` folder

2. Processing Pipeline
   - Run pose estimation for all participant pairs:
     ```bash
     python post_estimation_pose2sim.py
     ```
   - Generate visualization videos from the processed data:
     ```bash
     python generate_videos.py
     ```



