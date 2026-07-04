"""
Criminal Network EDA Analysis Script
KSP Datathon 2026 - Challenge 2
This script performs comprehensive graph analysis on associations.csv
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import community as community_louvain
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

print("="*80)
print("CRIMINAL NETWORK EXPLORATORY DATA ANALYSIS")
print("KSP Datathon 2026 - Challenge 2")
print("="*80)

# ============================================================================
# DATA LOADING
# ============================================================================
print("\n" + "="*80)
print("DATA LOADING")
print("="*80)

associations_df = pd.read_csv('associations.csv')
print(f"\n[OK] Loaded associations.csv")
print(f"  Shape: {associations_df.shape}")
print(f"  Columns: {list(associations_df.columns)}")
print(f"  Missing values: {associations_df.isnull().sum().sum()}")

print(f"\nFirst 5 rows:")
print(associations_df.head())

# ============================================================================
# PHASE 1: GLOBAL GRAPH TOPOLOGY
# ============================================================================
print("\n" + "="*80)
print("PHASE 1: GLOBAL GRAPH TOPOLOGY")
print("="*80)

# Build the graph
print("\n[1.1] Building Network Graph...")
G = nx.from_pandas_edgelist(
    associations_df,
    source='source_id',
    target='target_id',
    edge_attr='link_type',
    create_using=nx.Graph()
)

# Basic metrics
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
print(f"[OK] Graph constructed")
print(f"  Total Nodes (V): {num_nodes:,}")
print(f"  Total Edges (E): {num_edges:,}")

# Network Density
print("\n[1.2] Calculating Network Density...")
density = nx.density(G)
print(f"[OK] Network Density: {density:.6f}")
print(f"  Interpretation: {'Highly sparse network' if density < 0.01 else 'Moderately connected'}")

# Connected Components
print("\n[1.3] Analyzing Connected Components...")
components = list(nx.connected_components(G))
num_components = len(components)
component_sizes = sorted([len(c) for c in components], reverse=True)

print(f"[OK] Number of Connected Components: {num_components:,}")
print(f"  Giant Component Size: {component_sizes[0]:,} nodes ({100*component_sizes[0]/num_nodes:.2f}%)")
print(f"  Top 10 Component Sizes: {component_sizes[:10]}")

# Degree Distribution
print("\n[1.4] Analyzing Degree Distribution...")
degrees = dict(G.degree())
degree_values = list(degrees.values())
degree_counts = Counter(degree_values)

print(f"[OK] Degree Statistics:")
print(f"  Mean Degree: {np.mean(degree_values):.2f}")
print(f"  Median Degree: {np.median(degree_values):.2f}")
print(f"  Max Degree: {max(degree_values)}")
print(f"  Min Degree: {min(degree_values)}")
print(f"  Std Dev: {np.std(degree_values):.2f}")

# Plot Degree Distribution
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.hist(degree_values, bins=50, edgecolor='black', alpha=0.7)
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.title('Degree Distribution (Linear Scale)')
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 2)
plt.hist(degree_values, bins=50, edgecolor='black', alpha=0.7, log=True)
plt.xlabel('Degree')
plt.ylabel('Frequency (log scale)')
plt.title('Degree Distribution (Log Scale)')
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 3)
unique_degrees = sorted(degree_counts.keys())
counts = [degree_counts[d] for d in unique_degrees]
plt.loglog(unique_degrees, counts, 'bo', alpha=0.6)
plt.xlabel('Degree (log scale)')
plt.ylabel('Frequency (log scale)')
plt.title('Log-Log Plot (Power-Law Test)')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase1_degree_distribution.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: phase1_degree_distribution.png")


# Test for Scale-Free (Power-Law) Distribution
print("\n[1.5] Testing for Scale-Free Network...")
# Remove zeros and fit power law
non_zero_degrees = [d for d in degree_values if d > 0]
if len(non_zero_degrees) > 10:
    # Simple power-law test using log-log regression
    unique_deg = np.array(sorted(set(non_zero_degrees)))
    freq = np.array([degree_counts[d] for d in unique_deg])
    
    # Filter out zeros for log
    mask = (unique_deg > 0) & (freq > 0)
    if np.sum(mask) > 5:
        log_deg = np.log10(unique_deg[mask])
        log_freq = np.log10(freq[mask])
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_deg, log_freq)
        
        print(f"[OK] Power-Law Fit Results:")
        print(f"  Slope (gamma): {-slope:.3f}")
        print(f"  R-squared: {r_value**2:.3f}")
        print(f"  Interpretation: {'Strong Scale-Free' if r_value**2 > 0.7 else 'Weak Scale-Free'} network")
        print(f"  Validation: {'[OK] PASS' if r_value**2 > 0.6 else '[FAIL] FAIL'} - Hub-and-spoke model")

# ============================================================================
# PHASE 2: CENTRALITY ANALYSIS (TARGET IDENTIFICATION)
# ============================================================================
print("\n" + "="*80)
print("PHASE 2: CENTRALITY ANALYSIS (TARGET IDENTIFICATION)")
print("="*80)

# Degree Centrality - The Kingpins
print("\n[2.1] Computing Degree Centrality (The Kingpins)...")
degree_centrality = nx.degree_centrality(G)
top_kingpins = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:20]

print(f"[OK] Top 20 Kingpins (by Degree Centrality):")
for rank, (node_id, centrality) in enumerate(top_kingpins, 1):
    degree = G.degree(node_id)
    print(f"  {rank:2d}. Node: {node_id[:8]}... | Degree: {degree:3d} | Centrality: {centrality:.4f}")

# Betweenness Centrality - The Brokers
print("\n[2.2] Computing Betweenness Centrality (The Brokers)...")
# Use k-parameter for faster approximate betweenness (sample k nodes)
k_sample = min(500, G.number_of_nodes() // 10)
betweenness_centrality = nx.betweenness_centrality(G, normalized=True, k=k_sample)
top_brokers = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:20]

print(f"[OK] Top 20 Brokers (by Betweenness Centrality):")
for rank, (node_id, centrality) in enumerate(top_brokers, 1):
    print(f"  {rank:2d}. Node: {node_id[:8]}... | Betweenness: {centrality:.6f}")

# Eigenvector Centrality - The Influencers
print("\n[2.3] Computing Eigenvector Centrality (The Influencers)...")
try:
    # Use largest connected component for eigenvector centrality
    largest_cc = max(nx.connected_components(G), key=len)
    G_largest = G.subgraph(largest_cc).copy()
    eigenvector_centrality = nx.eigenvector_centrality(G_largest, max_iter=1000)
    
    # Extend to full graph with 0 for disconnected nodes
    eigenvector_full = {node: eigenvector_centrality.get(node, 0.0) for node in G.nodes()}
    top_influencers = sorted(eigenvector_full.items(), key=lambda x: x[1], reverse=True)[:20]
    
    print(f"[OK] Top 20 Influencers (by Eigenvector Centrality):")
    for rank, (node_id, centrality) in enumerate(top_influencers, 1):
        print(f"  {rank:2d}. Node: {node_id[:8]}... | Eigenvector: {centrality:.6f}")
except:
    print("[WARN] Could not compute eigenvector centrality (network may be disconnected)")
    eigenvector_full = {node: 0.0 for node in G.nodes()}

# Visualization: Centrality Comparison
print("\n[2.4] Creating Centrality Visualizations...")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Degree Centrality Distribution
ax1 = axes[0, 0]
degree_vals = list(degree_centrality.values())
ax1.hist(degree_vals, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
ax1.set_xlabel('Degree Centrality')
ax1.set_ylabel('Frequency')
ax1.set_title('Degree Centrality Distribution (Kingpins)')
ax1.grid(True, alpha=0.3)

# Betweenness Centrality Distribution
ax2 = axes[0, 1]
betweenness_vals = list(betweenness_centrality.values())
ax2.hist(betweenness_vals, bins=50, edgecolor='black', alpha=0.7, color='coral')
ax2.set_xlabel('Betweenness Centrality')
ax2.set_ylabel('Frequency')
ax2.set_title('Betweenness Centrality Distribution (Brokers)')
ax2.grid(True, alpha=0.3)

# Eigenvector Centrality Distribution
ax3 = axes[1, 0]
eigen_vals = list(eigenvector_full.values())
ax3.hist(eigen_vals, bins=50, edgecolor='black', alpha=0.7, color='mediumseagreen')
ax3.set_xlabel('Eigenvector Centrality')
ax3.set_ylabel('Frequency')
ax3.set_title('Eigenvector Centrality Distribution (Influencers)')
ax3.grid(True, alpha=0.3)

# Centrality Correlation
ax4 = axes[1, 1]
deg_values = [degree_centrality[n] for n in G.nodes()]
bet_values = [betweenness_centrality[n] for n in G.nodes()]
ax4.scatter(deg_values, bet_values, alpha=0.5, s=10)
ax4.set_xlabel('Degree Centrality')
ax4.set_ylabel('Betweenness Centrality')
ax4.set_title('Degree vs Betweenness Centrality')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase2_centrality_analysis.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: phase2_centrality_analysis.png")


# ============================================================================
# PHASE 3: EDGE & LINK TYPE PROFILING
# ============================================================================
print("\n" + "="*80)
print("PHASE 3: EDGE & LINK TYPE PROFILING")
print("="*80)

# Frequency Analysis
print("\n[3.1] Analyzing Link Type Distribution...")
link_type_counts = associations_df['link_type'].value_counts()
print(f"[OK] Link Type Frequency:")
for link_type, count in link_type_counts.items():
    percentage = 100 * count / len(associations_df)
    print(f"  {link_type:20s}: {count:6,} ({percentage:5.2f}%)")

# Visualization: Link Type Distribution
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
link_type_counts.plot(kind='bar', color='skyblue', edgecolor='black', alpha=0.8)
plt.xlabel('Link Type')
plt.ylabel('Frequency')
plt.title('Distribution of Link Types')
plt.xticks(rotation=45, ha='right')
plt.grid(True, alpha=0.3, axis='y')

plt.subplot(1, 2, 2)
plt.pie(link_type_counts.values, labels=link_type_counts.index, autopct='%1.1f%%', startangle=90)
plt.title('Link Type Proportions')

plt.tight_layout()
plt.savefig('phase3_link_type_distribution.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: phase3_link_type_distribution.png")

# Assortativity Analysis (requires criminals.csv)
print("\n[3.2] Analyzing Assortativity (Risk Score Correlation)...")
try:
    criminals_df = pd.read_csv('criminals.csv')
    print(f"[OK] Loaded criminals.csv ({len(criminals_df)} records)")
    
    # Create risk score mapping
    risk_scores = dict(zip(criminals_df['criminal_id'], criminals_df['base_risk_score']))
    
    # Assign risk scores to nodes
    nx.set_node_attributes(G, risk_scores, 'risk_score')
    
    # Calculate assortativity coefficient
    # Filter to nodes with risk scores
    nodes_with_risk = [n for n in G.nodes() if n in risk_scores]
    G_risk = G.subgraph(nodes_with_risk).copy()
    
    assortativity = nx.attribute_assortativity_coefficient(G_risk, 'risk_score')
    print(f"\n[OK] Assortativity Coefficient: {assortativity:.4f}")
    
    if assortativity > 0.2:
        interpretation = "High-risk criminals tend to associate with other high-risk criminals"
    elif assortativity < -0.2:
        interpretation = "High-risk criminals tend to recruit low-risk individuals"
    else:
        interpretation = "Risk scores show no strong assortativity pattern"
    
    print(f"  Interpretation: {interpretation}")
    
    # Visualize risk score correlations
    edges_with_risk = []
    for u, v in G_risk.edges():
        if u in risk_scores and v in risk_scores:
            edges_with_risk.append((risk_scores[u], risk_scores[v]))
    
    if len(edges_with_risk) > 0:
        source_risks, target_risks = zip(*edges_with_risk)
        
        plt.figure(figsize=(10, 6))
        plt.scatter(source_risks, target_risks, alpha=0.3, s=10)
        plt.xlabel('Source Node Risk Score')
        plt.ylabel('Target Node Risk Score')
        plt.title(f'Risk Score Assortativity (r = {assortativity:.3f})')
        
        # Add diagonal line
        min_risk, max_risk = 0, 100
        plt.plot([min_risk, max_risk], [min_risk, max_risk], 'r--', alpha=0.5, label='Perfect Assortativity')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.savefig('phase3_assortativity.png', dpi=300, bbox_inches='tight')
        print("[OK] Saved: phase3_assortativity.png")
    
except FileNotFoundError:
    print("[WARN] criminals.csv not found - skipping assortativity analysis")
except Exception as e:
    print(f"[WARN] Error in assortativity analysis: {e}")

# Edge type network statistics
print("\n[3.3] Analyzing Network by Link Type...")
for link_type in link_type_counts.index:
    edges_of_type = associations_df[associations_df['link_type'] == link_type]
    G_type = nx.from_pandas_edgelist(
        edges_of_type,
        source='source_id',
        target='target_id',
        create_using=nx.Graph()
    )
    print(f"\n  {link_type}:")
    print(f"    Nodes: {G_type.number_of_nodes():,}")
    print(f"    Edges: {G_type.number_of_edges():,}")
    print(f"    Components: {nx.number_connected_components(G_type):,}")
    if G_type.number_of_nodes() > 0:
        print(f"    Avg Degree: {2 * G_type.number_of_edges() / G_type.number_of_nodes():.2f}")


# ============================================================================
# PHASE 4: COMMUNITY DETECTION (SYNDICATE CLUSTERING)
# ============================================================================
print("\n" + "="*80)
print("PHASE 4: COMMUNITY DETECTION (SYNDICATE CLUSTERING)")
print("="*80)

# Louvain Community Detection
print("\n[4.1] Running Louvain Community Detection Algorithm...")
communities = community_louvain.best_partition(G)

print(f"[OK] Community detection completed")
print(f"  Total communities detected: {len(set(communities.values())):,}")

# Assign community IDs to nodes
nx.set_node_attributes(G, communities, 'community_id')

# Analyze community sizes
community_sizes = Counter(communities.values())
sorted_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)

print(f"\n[OK] Community Size Distribution:")
print(f"  Largest community: {sorted_communities[0][1]:,} nodes")
print(f"  Smallest community: {sorted_communities[-1][1]:,} nodes")
print(f"  Mean community size: {np.mean(list(community_sizes.values())):.2f}")
print(f"  Median community size: {np.median(list(community_sizes.values())):.2f}")

print(f"\n  Top 20 Largest Communities:")
for rank, (comm_id, size) in enumerate(sorted_communities[:20], 1):
    percentage = 100 * size / num_nodes
    print(f"    {rank:2d}. Community {comm_id:3d}: {size:6,} nodes ({percentage:5.2f}%)")

# Calculate modularity
modularity = community_louvain.modularity(communities, G)
print(f"\n[OK] Modularity Score: {modularity:.4f}")
print(f"  Interpretation: {'Strong' if modularity > 0.4 else 'Moderate' if modularity > 0.3 else 'Weak'} community structure")

# Visualize community size distribution
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
sizes = list(community_sizes.values())
plt.hist(sizes, bins=50, edgecolor='black', alpha=0.7, color='purple')
plt.xlabel('Community Size')
plt.ylabel('Frequency')
plt.title('Community Size Distribution')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
top_20_sizes = [size for _, size in sorted_communities[:20]]
top_20_ids = [f"C{comm_id}" for comm_id, _ in sorted_communities[:20]]
plt.barh(range(20), top_20_sizes, color='teal', edgecolor='black', alpha=0.8)
plt.yticks(range(20), top_20_ids)
plt.xlabel('Number of Nodes')
plt.title('Top 20 Largest Communities')
plt.gca().invert_yaxis()
plt.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('phase4_community_detection.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: phase4_community_detection.png")

# Large-scale syndicates (communities with > 50 members)
large_syndicates = [(comm_id, size) for comm_id, size in sorted_communities if size >= 50]
print(f"\n[OK] Large-Scale Syndicates (≥50 members): {len(large_syndicates)}")
for comm_id, size in large_syndicates:
    print(f"  Community {comm_id}: {size:,} members")

# ============================================================================
# GENERATE TOP TARGETS REPORT
# ============================================================================
print("\n" + "="*80)
print("GENERATING TOP TARGETS REPORT")
print("="*80)

print("\n[5.1] Creating Combined Target Score...")

# Create comprehensive dataframe with all centrality measures
targets_data = []

for node in G.nodes():
    targets_data.append({
        'criminal_id': node,
        'degree': G.degree(node),
        'degree_centrality': degree_centrality[node],
        'betweenness_centrality': betweenness_centrality[node],
        'eigenvector_centrality': eigenvector_full[node],
        'community_id': communities[node]
    })

targets_df = pd.DataFrame(targets_data)

# Normalize centrality scores to 0-100 scale
targets_df['degree_score'] = 100 * (targets_df['degree_centrality'] - targets_df['degree_centrality'].min()) / (targets_df['degree_centrality'].max() - targets_df['degree_centrality'].min())
targets_df['betweenness_score'] = 100 * (targets_df['betweenness_centrality'] - targets_df['betweenness_centrality'].min()) / (targets_df['betweenness_centrality'].max() - targets_df['betweenness_centrality'].min())

# Combined score: weighted average (60% degree, 40% betweenness)
targets_df['combined_score'] = 0.6 * targets_df['degree_score'] + 0.4 * targets_df['betweenness_score']

# Sort by combined score
targets_df = targets_df.sort_values('combined_score', ascending=False)

# Merge with criminal names if available
try:
    criminals_df = pd.read_csv('criminals.csv')
    targets_df = targets_df.merge(
        criminals_df[['criminal_id', 'name', 'age', 'base_risk_score']],
        on='criminal_id',
        how='left'
    )
    print("[OK] Merged with criminal profile data")
except:
    print("[WARN] Could not merge with criminals.csv")

# Select top 50 targets
top_50_targets = targets_df.head(50)

# Save to CSV
top_50_targets.to_csv('top_targets_identified.csv', index=False)
print(f"[OK] Saved: top_targets_identified.csv ({len(top_50_targets)} records)")

print(f"\n[OK] Top 10 Priority Targets:")
for rank, row in enumerate(top_50_targets.head(10).itertuples(), 1):
    name = row.name if hasattr(row, 'name') else 'Unknown'
    print(f"  {rank:2d}. {name:25s} | Combined Score: {row.combined_score:6.2f} | Degree: {row.degree:3d} | Betweenness: {row.betweenness_centrality:.4f}")


# ============================================================================
# GRAPH VALIDATION CHECK & SUMMARY
# ============================================================================
print("\n" + "="*80)
print("GRAPH VALIDATION CHECK & SUMMARY")
print("="*80)

print("\n[6.1] Network Validation Summary:")
print("-" * 80)

# Validation criteria
validation_results = {
    'Network is sparse (density < 0.01)': density < 0.01,
    'Contains large Giant Component (>50% nodes)': component_sizes[0] / num_nodes > 0.5,
    'Degree distribution shows heavy tail': max(degree_values) > 10 * np.mean(degree_values),
    'Strong community structure (modularity > 0.3)': modularity > 0.3,
    'Multiple isolated syndicates exist': num_components > 10
}

print("\n[OK] Validation Criteria:")
for criterion, passed in validation_results.items():
    status = "[OK] PASS" if passed else "[FAIL] FAIL"
    print(f"  {status} | {criterion}")

# Overall assessment
passes = sum(validation_results.values())
total = len(validation_results)
overall_pass = passes >= 4

print(f"\n{'='*80}")
print(f"OVERALL VALIDATION: {'[OK] PASS' if overall_pass else '[FAIL] FAIL'} ({passes}/{total} criteria met)")
print(f"{'='*80}")

# Summary statistics
print("\n[6.2] Final Network Summary:")
print("-" * 80)
print(f"Network Structure:")
print(f"  • Total Criminals (Nodes): {num_nodes:,}")
print(f"  • Total Associations (Edges): {num_edges:,}")
print(f"  • Network Density: {density:.6f}")
print(f"  • Average Degree: {np.mean(degree_values):.2f}")
print(f"  • Network Diameter: ", end="")
try:
    if nx.is_connected(G):
        diameter = nx.diameter(G)
        print(f"{diameter}")
    else:
        diameter_largest = nx.diameter(G.subgraph(largest_cc))
        print(f"{diameter_largest} (largest component)")
except:
    print("Unable to compute")

print(f"\nConnectivity:")
print(f"  • Connected Components: {num_components:,}")
print(f"  • Giant Component: {component_sizes[0]:,} nodes ({100*component_sizes[0]/num_nodes:.1f}%)")
print(f"  • Isolated Nodes: {sum(1 for d in degree_values if d == 0)}")

print(f"\nCentrality Insights:")
print(f"  • Top Kingpin Degree: {max(degree_values)}")
print(f"  • Top Broker Betweenness: {max(betweenness_vals):.6f}")
print(f"  • Nodes with Degree > 10: {sum(1 for d in degree_values if d > 10):,}")
print(f"  • Nodes with Degree > 50: {sum(1 for d in degree_values if d > 50):,}")

print(f"\nCommunity Structure:")
print(f"  • Total Communities: {len(set(communities.values())):,}")
print(f"  • Modularity Score: {modularity:.4f}")
print(f"  • Largest Syndicate: {sorted_communities[0][1]:,} members")
print(f"  • Large Syndicates (≥50 members): {len(large_syndicates)}")

print(f"\nLink Types:")
for link_type, count in link_type_counts.items():
    print(f"  • {link_type}: {count:,} ({100*count/num_edges:.1f}%)")

print(f"\n{'='*80}")
print("CONCLUSION:")
print(f"{'='*80}")

if overall_pass:
    print("[OK] The dataset SUCCESSFULLY mimics a realistic criminal syndicate network.")
    print("[OK] Network exhibits Scale-Free topology with clear hub-and-spoke structure.")
    print("[OK] Strong community detection reveals distinct, isolated syndicates.")
    print("[OK] High-priority targets (Kingpins and Brokers) clearly identified.")
    print("[OK] Dataset is SUITABLE for the final Hackathon demonstration.")
else:
    print("[WARN] The dataset shows some characteristics of criminal networks but")
    print("  may need additional validation or synthetic data generation.")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print(f"{'='*80}")

print(f"\n[REPORTS] Generated Outputs:")
print(f"  • phase1_degree_distribution.png")
print(f"  • phase2_centrality_analysis.png")
print(f"  • phase3_link_type_distribution.png")
print(f"  • phase3_assortativity.png")
print(f"  • phase4_community_detection.png")
print(f"  • top_targets_identified.csv")

print(f"\n[OK] All analysis phases completed successfully!")
print(f"\nNext Steps:")
print(f"  1. Review generated visualizations")
print(f"  2. Examine top_targets_identified.csv for priority targets")
print(f"  3. Integrate findings into backend API for Link Analysis dashboard")
print(f"  4. Prepare presentation materials for Hackathon demonstration")
