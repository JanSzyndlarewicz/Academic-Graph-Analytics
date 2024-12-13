# Citation Graph Analysis

## Overview
Analyzing abstract characteristics of the scientific community, such as the degree of connectedness of its subfields, can be achieved through graph theory. By constructing a graph linking scientific papers through their citations and utilizing metadata features, we can uncover insights into the connections between different fields, institutions, and researchers. 

Collected data can be decomposed by country, university, field, or time to explore various aspects of scientific collaboration and dynamics.

## Research summary
https://www.canva.com/design/DAGY23xkLjQ/nEcLd0XOMpk_8GuJwdgMHg/edit?utm_content=DAGY23xkLjQ&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton


![image](https://github.com/user-attachments/assets/3f1e45c4-6e67-41ed-a6a7-908f4bde5d60)
<img width="965" alt="image" src="https://github.com/user-attachments/assets/d6738ed1-1bdc-44fe-b9cc-5705e2e73868" />
<img width="930" alt="image" src="https://github.com/user-attachments/assets/6d8a487b-c65a-4821-b14a-83860b021cff" />
![image](https://github.com/user-attachments/assets/8918a0da-c7b3-4bef-825f-85e94333ec71)


## Problem Statements

### Problem Statement 1: Geopolitical Conflicts and Academic Bias
**Aim**: Evaluate the extent to which the geopolitical conflict of the Russian invasion of Ukraine affects the attitude of the international research community towards Russian researchers.

**Objectives**:
- Quantify changes in citation patterns for Russian-affiliated research.
- Examine geographic variations in citation trends.
- Identify citation bias indicators in high-impact journals.

**Methodology**:
1. **Data Collection**: Papers and citations for 7 countries and top 10 universities for each country.
2. **Data Processing**: Standardize and clean data.
3. **Analysis of Citation Patterns**: Compare trends over time.
4. **Visualization and Interpretation**: Present insights in an intuitive format.

### Problem Statement 2: Dynamics Between Scientific Fields
**Aim**: Investigate scholarly articles to evaluate the dynamics between various fields and/or individual scientists using citation data as a measure of connectedness.

**Objectives**:
- Examine the degree of overlap between research fields.
- Analyze geographic variations in citation trends.
- Determine trends for specific researchers using PageRank over time.

**Output Data**:
- Degree of connectedness between fields.
- Interdisciplinary collaboration metrics.
- Clusters and trends for further investigation.

### Problem Statement 3: Detection of Academic Cliques
**Aim**: Identify tightly connected clusters of researchers potentially engaging in citation inflation.

**Objectives**:
- Investigate unusually tightly connected communities.
- Detect clusters with minimal connections to other communities.

**Scope**:
- Subset of research articles constrained by time, geography, and fields.
- Subset of researcher networks.

## Tools and Techniques
- APIs: Scopus, CrossRef, Semantic Scholar
- Graph Analysis: Clustering techniques, community detection, temporal analysis
- Visualization: Dashboard development for insights presentation

## Research Directions
- Investigate the overall structure and properties of citation graphs.
- Determine the degree of connectedness and check for separable communities based on field, country, or institution.
- Analyze changes in citation dynamics in response to world events.
- Explore interdisciplinary areas by identifying connections between different fields.

## Methodology
### Field Connectedness
**Without Field Feature**:
- Encode paper keywords as features.
- Extend the graph using BFS to find overlap between fields A and B.

**With Field Feature**:
- Cluster papers and analyze diversity of fields in clusters.
- Use BFS to measure interdisciplinary collaboration.
- Identify high betweenness centrality nodes as connectors between fields.

### War Implications on Academic Bias
- Select top 10 Russian institutions and 3-5 key fields.
- Collect citation data for papers.
- Analyze geographic and temporal citation trends.

## Challenges
- **Limited API Availability**: Google Scholar lacks a public API, and Scopus imposes strict request limits.
- **Data Inconsistency**: Variations in data formats between APIs.
- **Data Completeness**: Missing fields like DOIs in some datasets.
- **High Filtering Rates**: Many citations fall outside the problem scope.
- **Integration Complexity**: Merging large datasets from multiple APIs.

## Preliminary Results
1. No statistically significant evidence of variation in academic citation patterns related to the invasion was found.
2. A downward trend in centrality metrics for Russian research output over the past five years was observed, but causes remain unclear.
3. Russian researchers form tighter collaborative clusters compared to their Western counterparts.
4. Academic clusters often align with geopolitical factors.

## Future Tasks
- Identify similar past studies for reference.
- Expand datasets and refine analysis techniques.
- Develop an interactive dashboard for data visualization.


# How to start

1. Create `.env` file in the root directory and add the following variables:
```
SEMANTIC_SCHOLAR_API_KEY=your_api_key
NEO4J_USER=username
NEO4J_PASSWORD=password
```

2. Install requirements
```bash
pip install -r requirements.txt
```

# Pre-commit Hooks
This project uses `pre-commit` to ensure consistent formatting and quality checks.

## How to Enable Pre-commit
1. Install pre-commit
```bash
pip install pre-commit
```

2. Install pre-commit hooks
```bash
pre-commit install
```

### How to disable pre-commit
```bash
pre-commit uninstall
```
